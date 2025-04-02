import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "http://localhost:8000/openapi.json",
  output: { path: "src/client", format: "prettier", lint: "eslint" },
  plugins: [
    {
      name: "@hey-api/client-fetch",
      runtimeConfigPath: "./src/misc/hey-api.ts",
    },
  ],
});
