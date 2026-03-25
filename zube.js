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
  {
    name: "get_project_members",
    description: "Get a list of members for a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },

  // ── Epics ──────────────────────────────────────────────────────────────────

  {
    name: "get_epics",
    description: "Get a list of epics for a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "create_epic",
    description: "Create an epic in a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        title: { type: "string", description: "Epic title" },
        description: { type: "string", description: "Epic description" },
        assignee_id: { type: "number", description: "Assignee user ID" },
        due_on: { type: "string", description: "Due date (ISO timestamp)" },
        color: { type: "string", description: "Hex color code without preceding '#'" },
        epic_list_id: { type: "number", description: "Epic list ID" },
        label_ids: { type: "array", items: { type: "number" }, description: "Array of label IDs" },
        track_cards: { type: "boolean", description: "Whether to track cards" },
        target_position: { type: "number", description: "Target index position of the epic" },
        after_target_id: { type: "number", description: "Place epic after this epic ID" },
        before_target_id: { type: "number", description: "Place epic before this epic ID" },
      },
      required: ["project_id", "title"],
    },
  },
  {
    name: "get_epic",
    description: "Get a single epic by ID",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        epic_id: { type: "number", description: "The epic ID" },
      },
      required: ["project_id", "epic_id"],
    },
  },
  {
    name: "update_epic",
    description: "Update an epic",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        epic_id: { type: "number", description: "The epic ID" },
        title: { type: "string", description: "Epic title" },
        description: { type: "string", description: "Epic description" },
        assignee_id: { type: "number", description: "Assignee user ID" },
        due_on: { type: "string", description: "Due date (ISO timestamp)" },
        color: { type: "string", description: "Hex color code without preceding '#'" },
        epic_list_id: { type: "number", description: "Epic list ID" },
        label_ids: { type: "array", items: { type: "number" }, description: "Array of label IDs" },
        track_cards: { type: "boolean", description: "Whether to track cards" },
        state: { type: "string", enum: ["open", "closed"], description: "Epic state" },
        status: {
          type: "string",
          enum: ["new", "queued", "in_progress", "completed", "closed", "archived"],
          description: "Epic status",
        },
      },
      required: ["project_id", "epic_id", "title", "description", "assignee_id", "due_on", "color", "epic_list_id", "label_ids", "track_cards", "state", "status"],
    },
  },
  {
    name: "move_epic",
    description: "Move an epic within a project. Provide only one of target_position, after_target_id, or before_target_id.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        epic_id: { type: "number", description: "The epic ID" },
        title: { type: "string", description: "Epic title" },
        description: { type: "string", description: "Epic description" },
        assignee_id: { type: "number", description: "Assignee user ID" },
        due_on: { type: "string", description: "Due date (ISO timestamp)" },
        color: { type: "string", description: "Hex color code without preceding '#'" },
        epic_list_id: { type: "number", description: "Epic list ID" },
        label_ids: { type: "array", items: { type: "number" }, description: "Array of label IDs" },
        track_cards: { type: "boolean", description: "Whether to track cards" },
        state: { type: "string", enum: ["open", "closed"], description: "Epic state" },
        status: {
          type: "string",
          enum: ["new", "queued", "in_progress", "completed", "closed", "archived"],
          description: "Epic status",
        },
        target_position: { type: "number", description: "Target index position" },
        after_target_id: { type: "number", description: "Place epic after this epic ID" },
        before_target_id: { type: "number", description: "Place epic before this epic ID" },
      },
      required: ["project_id", "epic_id", "title", "description", "assignee_id", "due_on", "color", "epic_list_id", "label_ids", "track_cards", "state", "status"],
    },
  },
  {
    name: "get_epic_cards",
    description: "Get a list of cards belonging to an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
      },
      required: ["epic_id"],
    },
  },
  {
    name: "add_card_to_epic",
    description: "Add a card to an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
        card_id: { type: "number", description: "The card ID to add" },
      },
      required: ["epic_id", "card_id"],
    },
  },
  {
    name: "remove_card_from_epic",
    description: "Remove a card from an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
        card_id: { type: "number", description: "The card ID to remove" },
      },
      required: ["epic_id", "card_id"],
    },
  },
  {
    name: "get_epic_comments",
    description: "Get a list of comments on an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
      },
      required: ["epic_id"],
    },
  },
  {
    name: "create_epic_comment",
    description: "Create a comment on an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
        body: { type: "string", description: "Comment text" },
      },
      required: ["epic_id", "body"],
    },
  },
  {
    name: "update_epic_comment",
    description: "Update a comment on an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
        comment_id: { type: "number", description: "The comment ID" },
        body: { type: "string", description: "Updated comment text" },
      },
      required: ["epic_id", "comment_id", "body"],
    },
  },
  {
    name: "delete_epic_comment",
    description: "Delete a comment from an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
        comment_id: { type: "number", description: "The comment ID" },
      },
      required: ["epic_id", "comment_id"],
    },
  },
  {
    name: "get_epic_events",
    description: "Get a list of events for an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
      },
      required: ["epic_id"],
    },
  },
  {
    name: "get_epic_subscriptions",
    description: "Get subscriptions for an epic (returns zero or one subscription for the current user)",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
      },
      required: ["epic_id"],
    },
  },
  {
    name: "create_epic_subscription",
    description: "Subscribe to an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
      },
      required: ["epic_id"],
    },
  },
  {
    name: "delete_epic_subscription",
    description: "Unsubscribe from an epic",
    inputSchema: {
      type: "object",
      properties: {
        epic_id: { type: "number", description: "The epic ID" },
        subscription_id: { type: "number", description: "The subscription ID" },
      },
      required: ["epic_id", "subscription_id"],
    },
  },

  // ── Epic Lists ─────────────────────────────────────────────────────────────

  {
    name: "get_epic_lists",
    description: "Get a list of epic lists for a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "create_epic_list",
    description: "Create an epic list in a project. Provide only one of target_position, after_target_id, or before_target_id.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        name: { type: "string", description: "Epic list name" },
        target_position: { type: "number", description: "Target index position" },
        after_target_id: { type: "number", description: "Place list after this epic list ID" },
        before_target_id: { type: "number", description: "Place list before this epic list ID" },
      },
      required: ["project_id", "name"],
    },
  },
  {
    name: "get_epic_list",
    description: "Get a single epic list by ID",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        epic_list_id: { type: "number", description: "The epic list ID" },
      },
      required: ["project_id", "epic_list_id"],
    },
  },
  {
    name: "update_epic_list",
    description: "Update an epic list",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        epic_list_id: { type: "number", description: "The epic list ID" },
        name: { type: "string", description: "Epic list name" },
      },
      required: ["project_id", "epic_list_id", "name"],
    },
  },
  {
    name: "move_epic_list",
    description: "Move an epic list within a project. Provide only one of target_position, after_target_id, or before_target_id.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        epic_list_id: { type: "number", description: "The epic list ID" },
        target_position: { type: "number", description: "Target index position" },
        after_target_id: { type: "number", description: "Place list after this epic list ID" },
        before_target_id: { type: "number", description: "Place list before this epic list ID" },
      },
      required: ["project_id", "epic_list_id"],
    },
  },
  {
    name: "delete_epic_list",
    description: "Delete an epic list",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        epic_list_id: { type: "number", description: "The epic list ID" },
      },
      required: ["project_id", "epic_list_id"],
    },
  },

  // ── Projects ───────────────────────────────────────────────────────────────

  {
    name: "create_project",
    description: "Create a new project",
    inputSchema: {
      type: "object",
      properties: {
        account_id: { type: "number", description: "The account ID" },
        name: { type: "string", description: "Project name" },
        description: { type: "string", description: "Project description" },
      },
      required: ["account_id", "name"],
    },
  },
  {
    name: "get_project",
    description: "Get a single project by ID",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "update_project",
    description: "Update a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        name: { type: "string", description: "Project name" },
        description: { type: "string", description: "Project description" },
        color: { type: "string", description: "Hex color code without preceding '#'" },
        auto_add_github_users: { type: "boolean", description: "Auto-add GitHub users" },
        should_use_fibonacci_scale: { type: "boolean", description: "Use Fibonacci scale for points" },
        triage: { type: "boolean", description: "Enable triage (only valid for projects with one workspace)" },
      },
      required: ["project_id", "name"],
    },
  },
  {
    name: "delete_project",
    description: "Delete a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "get_triage_cards",
    description: "Get a list of cards in a project's triage",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "get_project_milestones",
    description: "Get a list of milestones for a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },

  // ── Project Admins ─────────────────────────────────────────────────────────

  {
    name: "get_project_admins",
    description: "Get a list of admin members for a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "add_project_admin",
    description: "Add an admin to a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        person_id: { type: "number", description: "The person ID to add as admin" },
      },
      required: ["project_id", "person_id"],
    },
  },
  {
    name: "remove_project_admin",
    description: "Remove an admin from a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        person_id: { type: "number", description: "The person ID to remove as admin" },
      },
      required: ["project_id", "person_id"],
    },
  },

  // ── Project Members ────────────────────────────────────────────────────────

  {
    name: "add_project_member",
    description: "Add a member to a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        person_id: { type: "number", description: "The person ID to add as member" },
      },
      required: ["project_id", "person_id"],
    },
  },
  {
    name: "remove_project_member",
    description: "Remove a member from a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        person_id: { type: "number", description: "The person ID to remove" },
      },
      required: ["project_id", "person_id"],
    },
  },

  // ── Project Collaborators ──────────────────────────────────────────────────

  {
    name: "get_project_collaborators",
    description: "Get a list of collaborators for a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },

  // ── Customers ──────────────────────────────────────────────────────────────

  {
    name: "get_customers",
    description: "Get a list of customers for a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
      },
      required: ["project_id"],
    },
  },
  {
    name: "add_customer",
    description: "Add a customer to a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        name: { type: "string", description: "Customer name" },
        contact: { type: "string", description: "Customer contact info" },
      },
      required: ["project_id", "name"],
    },
  },
  {
    name: "get_customer",
    description: "Get a single customer by ID",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        customer_id: { type: "number", description: "The customer ID" },
      },
      required: ["project_id", "customer_id"],
    },
  },
  {
    name: "update_customer",
    description: "Update a customer",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        customer_id: { type: "number", description: "The customer ID" },
        name: { type: "string", description: "Customer name" },
        contact: { type: "string", description: "Customer contact info" },
      },
      required: ["project_id", "customer_id", "name"],
    },
  },
  {
    name: "remove_customer",
    description: "Remove a customer from a project",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "number", description: "The project ID" },
        customer_id: { type: "number", description: "The customer ID" },
      },
      required: ["project_id", "customer_id"],
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

    } else if (name === "get_project_members") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/members`);

    } else if (name === "move_card") {
      const destination = {
        type: args.destination_type,
        position: args.destination_position,
        ...(args.destination_name && { name: args.destination_name }),
        ...(args.destination_workspace_id && { workspace_id: args.destination_workspace_id }),
      };
      data = await zubeRequest("PUT", `/cards/${args.card_id}/move`, { destination });

    // ── Epics ────────────────────────────────────────────────────────────────

    } else if (name === "get_epics") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/epics`);

    } else if (name === "create_epic") {
      const { project_id, ...body } = args;
      data = await zubeRequest("POST", `/projects/${project_id}/epics`, body);

    } else if (name === "get_epic") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/epics/${args.epic_id}`);

    } else if (name === "update_epic") {
      const { project_id, epic_id, ...body } = args;
      data = await zubeRequest("PUT", `/projects/${project_id}/epics/${epic_id}`, body);

    } else if (name === "move_epic") {
      const { project_id, epic_id, ...body } = args;
      data = await zubeRequest("PUT", `/projects/${project_id}/epics/${epic_id}/move`, body);

    } else if (name === "get_epic_cards") {
      data = await zubeRequest("GET", `/epics/${args.epic_id}/cards`);

    } else if (name === "add_card_to_epic") {
      data = await zubeRequest("POST", `/epics/${args.epic_id}/cards`, { card_id: args.card_id });

    } else if (name === "remove_card_from_epic") {
      data = await zubeRequest("DELETE", `/epics/${args.epic_id}/cards/${args.card_id}`);

    } else if (name === "get_epic_comments") {
      data = await zubeRequest("GET", `/epics/${args.epic_id}/comments`);

    } else if (name === "create_epic_comment") {
      data = await zubeRequest("POST", `/epics/${args.epic_id}/comments`, { body: args.body });

    } else if (name === "update_epic_comment") {
      data = await zubeRequest("PUT", `/epics/${args.epic_id}/comments/${args.comment_id}`, { body: args.body });

    } else if (name === "delete_epic_comment") {
      data = await zubeRequest("DELETE", `/epics/${args.epic_id}/comments/${args.comment_id}`);

    } else if (name === "get_epic_events") {
      data = await zubeRequest("GET", `/epics/${args.epic_id}/events`);

    } else if (name === "get_epic_subscriptions") {
      data = await zubeRequest("GET", `/epics/${args.epic_id}/subscriptions`);

    } else if (name === "create_epic_subscription") {
      data = await zubeRequest("POST", `/epics/${args.epic_id}/subscriptions`);

    } else if (name === "delete_epic_subscription") {
      data = await zubeRequest("DELETE", `/epics/${args.epic_id}/subscriptions/${args.subscription_id}`);

    // ── Epic Lists ───────────────────────────────────────────────────────────

    } else if (name === "get_epic_lists") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/epic_lists`);

    } else if (name === "create_epic_list") {
      const { project_id, ...body } = args;
      data = await zubeRequest("POST", `/projects/${project_id}/epic_lists`, body);

    } else if (name === "get_epic_list") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/epic_lists/${args.epic_list_id}`);

    } else if (name === "update_epic_list") {
      const { project_id, epic_list_id, ...body } = args;
      data = await zubeRequest("PUT", `/projects/${project_id}/epic_lists/${epic_list_id}`, body);

    } else if (name === "move_epic_list") {
      const { project_id, epic_list_id, ...body } = args;
      data = await zubeRequest("PUT", `/projects/${project_id}/epic_lists/${epic_list_id}/move`, body);

    } else if (name === "delete_epic_list") {
      data = await zubeRequest("DELETE", `/projects/${args.project_id}/epic_lists/${args.epic_list_id}`);

    // ── Projects ─────────────────────────────────────────────────────────────

    } else if (name === "create_project") {
      data = await zubeRequest("POST", "/projects", args);

    } else if (name === "get_project") {
      data = await zubeRequest("GET", `/projects/${args.project_id}`);

    } else if (name === "update_project") {
      const { project_id, ...body } = args;
      data = await zubeRequest("PUT", `/projects/${project_id}`, body);

    } else if (name === "delete_project") {
      data = await zubeRequest("DELETE", `/projects/${args.project_id}`);

    } else if (name === "get_triage_cards") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/triage_cards`);

    } else if (name === "get_project_milestones") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/milestones`);

    // ── Project Admins ────────────────────────────────────────────────────────

    } else if (name === "get_project_admins") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/admin_members`);

    } else if (name === "add_project_admin") {
      data = await zubeRequest("POST", `/projects/${args.project_id}/admin_members/${args.person_id}`, { person_id: args.person_id });

    } else if (name === "remove_project_admin") {
      data = await zubeRequest("DELETE", `/projects/${args.project_id}/admin_members/${args.person_id}`);

    // ── Project Members ───────────────────────────────────────────────────────

    } else if (name === "add_project_member") {
      data = await zubeRequest("POST", `/projects/${args.project_id}/members`, { person_id: args.person_id });

    } else if (name === "remove_project_member") {
      data = await zubeRequest("DELETE", `/projects/${args.project_id}/members/${args.person_id}`);

    // ── Project Collaborators ─────────────────────────────────────────────────

    } else if (name === "get_project_collaborators") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/collaborators`);

    // ── Customers ─────────────────────────────────────────────────────────────

    } else if (name === "get_customers") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/customers`);

    } else if (name === "add_customer") {
      const { project_id, ...body } = args;
      data = await zubeRequest("POST", `/projects/${project_id}/customers`, body);

    } else if (name === "get_customer") {
      data = await zubeRequest("GET", `/projects/${args.project_id}/customers/${args.customer_id}`);

    } else if (name === "update_customer") {
      const { project_id, customer_id, ...body } = args;
      data = await zubeRequest("PUT", `/projects/${project_id}/customers/${customer_id}`, body);

    } else if (name === "remove_customer") {
      data = await zubeRequest("DELETE", `/projects/${args.project_id}/customers/${args.customer_id}`);

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