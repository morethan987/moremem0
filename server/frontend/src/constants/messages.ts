import { Message } from "@/types";

export const WELCOME_MESSAGE: Message = {
  id: "1",
  content: "👋 你好! 我是你的个人日程助手，有什么需要我做的吗？ 😊",
  sender: "assistant",
  timestamp: new Date().toLocaleTimeString(),
};

export const INVALID_CONFIG_MESSAGE: Message = {
  id: "2",
  content: "配置错误，请检查你的API keys是否输入，输入一个用户名然后再次尝试。",
  sender: "assistant",
  timestamp: new Date().toLocaleTimeString(),
};

export const ERROR_MESSAGE: Message = {
  id: "3",
  content: "未知错误，请稍后再试。",
  sender: "assistant",
  timestamp: new Date().toLocaleTimeString(),
};

export const AI_MODELS = {
  openai: "gpt-4o",
  anthropic: "claude-3-haiku-20240307",
  cohere: "command-r-plus",
  groq: "gemma2-9b-it",
  deepseek: "deepseek-chat",
  aliyun: "qwen-max-2025-01-25",
} as const;

export type Provider = keyof typeof AI_MODELS; 