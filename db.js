import sqlite3 from "sqlite3";
import { open } from "sqlite";

sqlite3.verbose();

const db = await open({
  filename: "./db.sqlite",
  driver: sqlite3.Database,
});

const createTableSQL = (tableName) => `
  CREATE TABLE IF NOT EXISTS ${tableName} (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt      TEXT NOT NULL,
    response    TEXT NOT NULL,
    correct_response TEXT NOT NULL,
    ROUGE-L_F1 DOUBLE,
    tool_invocation BOOL,
    correct_tool_invocation BOOL,
    tools_used  TEXT,
    correct_tool_use TEXT,
    tool_inputs TEXT,
    correct_tool_inputs TEXT,
    duration_ms INTEGER,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP  

  )
`;

await db.run(createTableSQL("chatgpt_tools"));
await db.run(createTableSQL("claude_tools"));
await db.run(createTableSQL("langchain_tools"));
await db.run(createTableSQL("mcp_tools"));

export default db;