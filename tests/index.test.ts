const path = require("path");
const analytics = require("../lib/index");
const { dateFromFilename, prepareForElasticSearch } = analytics;

const logs = {
  v1: {
    path: path.resolve(__dirname, "./logs/airboat_20130807_063622.txt"),
    date: new Date(Date.UTC(2013, 8, 7, 6, 36, 22))
  },
  v2: {
    path: path.resolve(__dirname, "./logs/airboat_20151220_043348.txt"),
    date: new Date(Date.UTC(2015, 12, 20, 4, 33, 48))
  },
  v3: {
    path: path.resolve(__dirname, "./logs/platypus_20160426_024734.txt"),
    date: new Date(Date.UTC(2016, 4, 26, 2, 47, 34))
  },
  v4: {
    path: path.resolve(__dirname, "./logs/platypus_20160519_013623.txt"),
    date: new Date(Date.UTC(2016, 5, 19, 1, 36, 23))
  }
};

describe("@platypus/analytics", () => {
  it("can be imported", () => {
    expect(analytics).toBeTruthy();
  });
});

describe("dateFromFilename", () => {
  for (const [type, log] of Object.entries(logs)) {
    it(`correctly parses ${type} log files`, () => {
      expect(dateFromFilename(log.path)).toEqual(log.date);
    });
  }
});

describe("prepareForElasticSearch", () => {
  it("correctly reformats v4 log files", async () => {
    prepareForElasticSearch(logs.v4.path, "/tmp/test.txt");
  });
});
