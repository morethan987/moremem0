import { MemoryConfig } from "../types";

export const DEFAULT_MEMORY_CONFIG: MemoryConfig = {
  version: "v1.1",
  embedder: {
    provider: "siliconflow",
    config: {
      apiKey: process.env.SILICONFLOW_API_KEY || "",
      model: "Pro/BAAI/bge-m3",
    },
  },
  vectorStore: {
    provider: "memory",
    config: {
      collectionName: "memories",
      dimension: 1024,
    },
  },
  llm: {
    provider: "aliyun",
    config: {
      apiKey: process.env.ALIYUN_API_KEY || "",
      model: "qwen-max-2025-01-25",
    },
  },
  enableGraph: false,
  graphStore: {
    provider: "neo4j",
    config: {
      url: process.env.NEO4J_URL || "neo4j://localhost:7687",
      username: process.env.NEO4J_USERNAME || "neo4j",
      password: process.env.NEO4J_PASSWORD || "password",
    },
    llm: {
      provider: "openai",
      config: {
        model: "gpt-4-turbo-preview",
      },
    },
  },
  historyDbPath: "memory.db",
};
