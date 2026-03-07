/**
 * Example Jest test — validates npm test / Jest setup.
 */
const { sum } = require("./sum");

describe("sum", () => {
  it("adds two numbers", () => {
    expect(sum(1, 2)).toBe(3);
  });

  it("returns 0 when both are 0", () => {
    expect(sum(0, 0)).toBe(0);
  });
});
