const fs = require("fs");
const readline = require("readline");
const utm = require("utm");

const LOGFILE_PATTERN = /.*(?:airboat|platypus)_(?<year>\d{4})(?<month>\d{2})(?<day>\d{2})_(?<hour>\d{2})(?<minute>\d{2})(?<second>\d{2}).txt$/;
const UTMZONE_PATTERN = /^(?<zone>\d+)(?<hemi>North|South)$/;

type Location = {
  latitude: number;
  longitude: number;
};

export const dateFromFilename = (path: string): Date => {
  // Attempt to parse the date pattern from the log name.
  const result = path.match(LOGFILE_PATTERN);
  if (!result) throw new Error(`File did not match Platypus log spec: ${path}`);

  // Convert the values from the date pattern into a UTC Date object.
  const { year, month, day, hour, minute, second } = result.groups!;
  return new Date(Date.UTC(+year, +month, +day, +hour, +minute, +second));
};

export const prepareForElasticSearch = async (
  inputPath: string,
  outputPath: string
) => {
  const input = fs.createReadStream(inputPath);
  const output = fs.createWriteStream(outputPath);

  try {
    const lines = readline.createInterface({ input, crlfDelay: Infinity });

    // Set up globals that will be constructed from the logfile.
    let start: Date | undefined;
    let location: Location | undefined;
    const vehicle = "Unknown"; // TODO: get this from the logs

    // Iterate through log messages to construct an elasticsearch log.
    for await (const line of lines) {
      const [millis, _level, message] = (line as string).split("\t");
      const payload = JSON.parse(message);

      // Update the date offset or compute the corrected timestamp.
      if (payload.date && payload.time) {
        start = new Date(payload.time - Number(millis));
        continue;
      } else if (!start) {
        throw new Error(`Datestamp must precede message: '${message}'`);
      }
      const time = start.getTime() + Number(millis);

      // If this is a pose message, update the current location estimate.
      if (payload.pose) {
        const easting = payload.pose.p[0];
        const northing = payload.pose.p[1];

        const pose = payload.pose.zone.match(UTMZONE_PATTERN);
        if (!pose)
          throw new Error(`Unable to interpret UTM zone: '${message}'`);
        const { zone, hemi } = pose.groups;

        location = utm.toLatLon(
          easting,
          northing,
          zone,
          undefined,
          hemi === "North",
          true
        );
        continue;
      }

      // If this is a sensor message, reformat it and append the time and location.
      // This is currently very hacky and special-cased for each sensor I know about.
      if (payload.sensor) {
        const { type, data, channel } = payload.sensor;
        const header = { time, ...location, channel };
        switch (type) {
          case "BATTERY":
            output.write(
              JSON.stringify({
                ...header,
                sensor: "battery",
                voltage: data[0]
              }) + "\n"
            );
            break;
          case "ES2":
            output.write(
              JSON.stringify({
                ...header,
                sensor: "es2",
                ec: data[0],
                temperature: data[1]
              }) + "\n"
            );
            break;
          case "ATLAS_DO":
            output.write(
              JSON.stringify({
                ...header,
                sensor: "atlas_do",
                oxygen: data[0]
              }) + "\n"
            );
            break;
          case "ATLAS_PH":
            output.write(
              JSON.stringify({
                ...header,
                sensor: "atlas_ph",
                ph: data[0]
              }) + "\n"
            );
            break;
          default:
            throw new Error(`Cannot handle sensor of type: '${type}'`);
        }
      }
    }
  } finally {
    // Always close the files even if we error.
    output.end();
    input.destroy();
  }
};
