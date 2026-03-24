import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { ListToolsRequestSchema, CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { fileURLToPath } from "url";
import path from "path";
import dotenv from "dotenv";
import fs from "fs";
import jsonwebtoken from "jsonwebtoken";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ quiet: true, path: path.join(__dirname, ".env") });

const server = new Server(
  { name: "zube-mcp-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

const client_id = process.env.ZUBE_CLIENT_ID;
const private_key = fs.readFileSync(path.join(__dirname, "zube_api_key.pem"));

let access_token = null;

function createRefreshJWT() {
  const now = Math.floor(Date.now() / 1000);
  return jsonwebtoken.sign(
    { iat: now, exp: now + 60, iss: client_id },
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

async function zubeRequest(method, path, body = null) {
  const token = await getValidAccessToken();

  const options = {
    method,
    headers: {
      Authorization: "Bearer " + token,
      "X-Client-ID": client_id,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  };
  if (body) options.body = JSON.stringify(body);

  let res = await fetch("https://zube.io/api" + path, options);

  if (res.status === 401) {
    access_token = await refreshToken();
    options.headers.Authorization = "Bearer " + access_token;
    res = await fetch("https://zube.io/api" + path, options);
  }

  return await res.json();
}

// ── Tool definitions ──────────────────────────────────────────────────────────

const TOOLS = [
  {
    name: "get_projects",
    description: "Fetch all projects from Zube",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "get_sprints",
    description: "Get a list of sprints for a workspace",
    inputSchema: {
      type: "object",
      properties: {
        workspace_id: { type: "number", description: "The workspace ID" },
      },
      required: ["workspace_id"],
    },
  },
  {
    name: "create_sprint",
    description: "Create a sprint in a workspace",
    inputSchema: {
      type: "object",
      properties: {
        workspace_id: { type: "number", description: "The workspace ID" },
        title: { type: "string", description: "Sprint title" },
        start_date: { type: "string", description: "Start date (ISO timestamp)" },
        end_date: { type: "string", description: "End date (ISO timestamp)" },
        description: { type: "string", description: "Optional description" },
      },
      required: ["workspace_id", "title", "start_date", "end_date"],
    },
  },
  {
    name: "get_sprint",
    description: "Get a single sprint by ID",
    inputSchema: {
      type: "object",
      properties: {
        workspace_id: { type: "number", description: "The workspace ID" },
        sprint_id: { type: "number", description: "The sprint ID" },
      },
      required: ["workspace_id", "sprint_id"],
    },
  },
  {
    name: "update_sprint",
    description: "Update a sprint",
    inputSchema: {
      type: "object",
      properties: {
        workspace_id: { type: "number", description: "The workspace ID" },
        sprint_id: { type: "number", description: "The sprint ID" },
        title: { type: "string", description: "Sprint title" },
        start_date: { type: "string", description: "Start date (ISO timestamp)" },
        end_date: { type: "string", description: "End date (ISO timestamp)" },
        description: { type: "string", description: "Description" },
        state: { type: "string", enum: ["open", "closed"], description: "Sprint state" },
      },
      required: ["workspace_id", "sprint_id", "title", "start_date", "end_date", "description", "state"],
    },
  },
  {
    name: "delete_sprint",
    description: "Delete a sprint",
    inputSchema: {
      type: "object",
      properties: {
        workspace_id: { type: "number", description: "The workspace ID" },
        sprint_id: { type: "number", description: "The sprint ID" },
      },
      required: ["workspace_id", "sprint_id"],
    },
  },
  {
    name: "get_sprint_events",
    description: "Get a list of events for a sprint",
    inputSchema: {
      type: "object",
      properties: {
        sprint_id: { type: "number", description: "The sprint ID" },
      },
      required: ["sprint_id"],
    },
  },
  {
    name: "get_project_cards",
    description: "Get a list of cards for a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "create_card",
    description: "Create a new card",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID (required)" },
        title: { type: "string", description: "Card title (required)" },
        body: { type: "string", description: "Card body text" },
        workspace_id: { type: "number", description: "Workspace ID" },
        sprint_id: { type: "number", description: "Sprint ID" },
        epic_id: { type: "number", description: "Epic ID" },
        assignee_ids: { type: "array", items: { type: "number" }, description: "Array of assignee IDs" },
        label_ids: { type: "array", items: { type: "number" }, description: "Array of label IDs" },
        points: { type: "number", description: "Story points" },
        priority: { type: "number", enum: [1, 2, 3, 4, 5], description: "Priority 1-5 or null" },
        category_name: { type: "string", description: "Category name" },
      },
      required: ["project_id", "title"],
    },
  },
  {
    name: "get_card",
    description: "Get a single card by ID",
    inputSchema: {
      type: "object",
      properties: {
        card_id: { type: "number", description: "The card ID" },
      },
      required: ["card_id"],
    },
  },
  {
    name: "update_card",
    description: "Update a card",
    inputSchema: {
      type: "object",
      properties: {
        card_id: { type: "number", description: "The card ID" },
        title: { type: "string", description: "Card title" },
        body: { type: "string", description: "Card body text" },
        project_id: { type: "number", description: "Project ID" },
        workspace_id: { type: "number", description: "Workspace ID" },
        sprint_id: { type: "number", description: "Sprint ID" },
        epic_id: { type: "number", description: "Epic ID" },
        assignee_ids: { type: "array", items: { type: "number" }, description: "Array of assignee IDs" },
        label_ids: { type: "array", items: { type: "number" }, description: "Array of label IDs" },
        points: { type: "number", description: "Story points" },
        priority: { type: "number", enum: [1, 2, 3, 4, 5], description: "Priority 1-5 or null" },
        state: { type: "string", enum: ["open", "closed"], description: "Card state" },
      },
      required: ["card_id"],
    },
  },
  {
    name: "archive_card",
    description: "Archive a card",
    inputSchema: {
      type: "object",
      properties: {
        card_id: { type: "number", description: "The card ID" },
      },
      required: ["card_id"],
    },
  },
  {
    name: "move_card",
    description: "Move a card to a workspace category or project triage",
    inputSchema: {
      type: "object",
      properties: {
        card_id: { type: "number", description: "The card ID" },
        destination_type: { type: "string", enum: ["category", "project"], description: "Destination type" },
        destination_position: { type: "number", description: "Position in the destination" },
        destination_name: { type: "string", description: "Category name (required if type is 'category')" },
        destination_workspace_id: { type: "number", description: "Workspace ID (required if type is 'category')" },
      },
      required: ["card_id", "destination_type", "destination_position"],
    },
  },
];

// ── Request handlers ──────────────────────────────────────────────────────────

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;

  try {
    let data;

    if (name === "get_projects") {
      data = await zubeRequest("GET", "/projects");

    } else if (name === "get_sprints") {
      data = await zubeRequest("GET", `/workspaces/${args.workspace_id}/sprints`);

    } else if (name === "create_sprint") {
      const { workspace_id, ...body } = args;
      data = await zubeRequest("POST", `/workspaces/${workspace_id}/sprints`, body);

    } else if (name === "get_sprint") {
      data = await zubeRequest("GET", `/workspaces/${args.workspace_id}/sprints/${args.sprint_id}`);

    } else if (name === "update_sprint") {
      const { workspace_id, sprint_id, ...body } = args;
      data = await zubeRequest("PUT", `/workspaces/${workspace_id}/sprints/${sprint_id}`, body);

    } else if (name === "delete_sprint") {
      data = await zubeRequest("DELETE", `/workspaces/${args.workspace_id}/sprints/${args.sprint_id}`);

    } else if (name === "get_sprint_events") {
      data = await zubeRequest("GET", `/sprints/${args.sprint_id}/events`);
      
    } else if (name === "get_project_cards") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/cards`);

    } else if (name === "create_card") {
      data = await zubeRequest("POST", "/cards", args);

    } else if (name === "get_card") {
      data = await zubeRequest("GET", `/cards/${args.card_id}`);

    } else if (name === "update_card") {
      const { card_id, ...body } = args;
      data = await zubeRequest("PUT", `/cards/${card_id}`, body);

    } else if (name === "archive_card") {
      data = await zubeRequest("PUT", `/cards/${args.card_id}/archive`);

    } else if (name === "move_card") {
      const destination = {
        type: args.destination_type,
        position: args.destination_position,
        ...(args.destination_name && { name: args.destination_name }),
        ...(args.destination_workspace_id && { workspace_id: args.destination_workspace_id }),
      };
      data = await zubeRequest("PUT", `/cards/${args.card_id}/move`, { destination });
    } else {
      throw new Error(`Unknown tool: ${name}`);
    }

    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  } catch (err) {
    return {
      content: [{ type: "text", text: `Error: ${err.message}` }],
    };
  }
});

// ── Start ─────────────────────────────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);