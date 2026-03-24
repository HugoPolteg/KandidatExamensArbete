import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js"; 
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import dotenv from "dotenv";
import fs from "fs";
import jsonwebtoken from "jsonwebtoken";
import { createRequire } from "module";
import { fileURLToPath } from "url";
import path from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ quiet: true, path: path.join(__dirname, ".env") });
const server = new Server(
  {
    name: "zube-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const client_id = process.env.ZUBE_CLIENT_ID;
const private_key = fs.readFileSync(path.join(__dirname, "zube_api_key.pem"));

let access_token = null;

function createRefreshJWT() {
  const now = Math.floor(Date.now() / 1000);

  return jsonwebtoken.sign(
    {
      iat: now,
      exp: now + 60,
      iss: client_id,
    },
    private_key,
    { algorithm: "RS256" }
  );
}

async function refreshToken() {
  const refresh_jwt = createRefreshJWT();

  const res = await fetch("https://zube.io/api/users/tokens", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + refresh_jwt,
      "X-Client-ID": client_id,
      Accept: "application/json",
    },
  });

  const data = await res.json();
  return data.access_token;
}

async function getValidAccessToken() {
  if (!access_token) {
    access_token = await refreshToken();
  }
  return access_token;
}

async function getProjects() {
  const token = await getValidAccessToken();

  const res = await fetch("https://zube.io/api/projects", {
    method: "GET",
    headers: {
      Authorization: "Bearer " + token,
      "X-Client-ID": client_id,
      Accept: "application/json",
    },
  });

  if (res.status === 401) {
    access_token = await refreshToken();

    const retry = await fetch("https://zube.io/api/projects", {
      method: "GET",
      headers: {
        Authorization: "Bearer " + access_token,
        "X-Client-ID": client_id,
        Accept: "application/json",
      },
    });

    return await retry.json();
  }

  return await res.json();
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_projects",
        description: "Fetch all projects from Zube",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  if (req.params.name === "get_projects") {
    try {
      const data = await getProjects();

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data, null, 2),
          },
        ],
      };
    } catch (err) {
      return {
        content: [
          {
            type: "text",
            text: `Error: ${err.message}`,
          },
        ],
      };
    }
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);