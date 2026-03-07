/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: "node",
  testMatch: ["**/scripts/js/**/*.test.js", "**/frontend/**/*.test.js", "**/*.test.js"],
  collectCoverageFrom: ["scripts/js/**/*.js", "frontend/src/**/*.js"].filter(Boolean),
  coverageDirectory: "coverage-js",
  verbose: true,
};
