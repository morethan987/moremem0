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
      dimension: 1536,
    },
  },
  llm: {
    provider: "aliyun",
    config: {
      apiKey: process.env.ALIYUN_API_KEY || "",
      model: "qwen-max-2025-01-25",
    },
  },
  historyDbPath: "memory.db",
};
