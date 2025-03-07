import dotenv from "dotenv";
import { createMem0 } from "../src";

dotenv.config();

export interface Provider {
  name: string;
  activeModel: string;
  apiKey: string | undefined;
}

export const testConfig = {
  apiKey: process.env.MEM0_API_KEY,
  userId: "test-sdk-morethan",
  deleteId: "test-sdk-morethan",
  providers: [
    // {
    //   name: "openai",
    //   activeModel: "gpt-4-turbo",
    //   apiKey: process.env.OPENAI_API_KEY,
    // }
    // , 
    // {
    //   name: "anthropic",
    //   activeModel: "claude-3-5-sonnet-20240620",
    //   apiKey: process.env.ANTHROPIC_API_KEY,
    // },
    // {
    //   name: "groq",
    //   activeModel: "gemma2-9b-it",
    //   apiKey: process.env.GROQ_API_KEY,
    // },
    // {
    //   name: "cohere",
    //   activeModel: "command-r-plus",
    //   apiKey: process.env.COHERE_API_KEY,
    // },
    // {
    //   name: "deepseek",
    //   activeModel: "deepseek-chat",
    //   apiKey: process.env.DEEPSEEK_API_KEY,
    // },
    {
      name: "aliyun",
      activeModel: "qwen-max-2025-01-25",
      apiKey: process.env.ALIYUN_API_KEY,
    },
  ],
  models: {
    openai: "gpt-4-turbo",
    anthropic: "claude-3-haiku-20240307",
    groq: "gemma2-9b-it",
    cohere: "command-r-plus",
    deepseek: "deepseek-chat",
    aliyun: "qwen-max-2025-01-25",
  },
  apiKeys: {
    openai: process.env.OPENAI_API_KEY,
    anthropic: process.env.ANTHROPIC_API_KEY,
    groq: process.env.GROQ_API_KEY,
    cohere: process.env.COHERE_API_KEY,
    deepseek: process.env.DEEPSEEK_API_KEY,
    aliyun: process.env.ALIYUN_API_KEY,
  },

  createTestClient: (provider: Provider) => {
    return createMem0({
      provider: provider.name,
      mem0ApiKey: process.env.MEM0_API_KEY,
      apiKey: provider.apiKey,
    });
  },
  deleteUser: async function () {
    if (!this.deleteId) {
      console.error("deleteId is not set. Ensure fetchDeleteId is called first.");
      return;
    }

    const options = {
      method: 'DELETE',
      headers: {
        Authorization: `Token ${this.apiKey}`,
      },
    };

    try {
      const response = await fetch(`http://localhost:8000/memories?user_id=${this.deleteId}`, options);
      if (!response.ok) {
        throw new Error(`Failed to delete user: ${response.statusText}`);
      }
      await response.json();
    } catch (error) {
      console.error("Error deleting user:", error);
      throw error;
    }
  },
};
