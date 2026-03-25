import sqlite3 from "sqlite3";
import { open } from "sqlite";

sqlite3.verbose();

const db = await open({
  filename: "./db.sqlite",
  driver: sqlite3.Database,
});

// reference_prompts must be created first since other tables reference it
await db.run(`
  CREATE TABLE IF NOT EXISTS prompts (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt                  TEXT NOT NULL,
    correct_response        TEXT,
    correct_tool_invocation BOOL,
    correct_tool_use        TEXT,
    correct_tool_inputs     TEXT
  )
`);

const createTableSQL = (tableName) => `
  CREATE TABLE IF NOT EXISTS ${tableName} (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id               INTEGER REFERENCES prompts(id),
    response                TEXT NOT NULL,
    rouge_l_f1              DOUBLE,
    tool_invocation         BOOL,
    tools_used              TEXT,
    tool_inputs             TEXT,
    duration_ms             INTEGER,
    timestamp               DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`;

await db.run(createTableSQL("chatgpt_tools"));
await db.run(createTableSQL("claude_tools"));
await db.run(createTableSQL("langchain_tools"));
await db.run(createTableSQL("mcp_tools"));

export default db;