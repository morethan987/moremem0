import OpenAI from "openai";
import { LLM, LLMResponse } from "./base";
import { LLMConfig, Message } from "../types";

export class AliyunLLM implements LLM {
  private aliyun: OpenAI;
  private model: string;

  constructor(config: LLMConfig) {
    this.aliyun = new OpenAI({
      apiKey: config.apiKey,
      baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    });
    this.model = config.model || "qwen-max-2025-01-25";
  }

  async generateResponse(
    messages: Message[],
    responseFormat?: { type: string },
  ): Promise<string> {
    const completion = await this.aliyun.chat.completions.create({
      messages: messages.map((msg) => ({
        role: msg.role as "system" | "user" | "assistant",
        content: msg.content,
      })),
      model: this.model,
      response_format: responseFormat as { type: "text" | "json_object" },
    });
    return completion.choices[0].message.content || "";
  }

  async generateChat(messages: Message[]): Promise<LLMResponse> {
    const completion = await this.aliyun.chat.completions.create({
      messages: messages.map((msg) => ({
        role: msg.role as "system" | "user" | "assistant",
        content: msg.content,
      })),
      model: this.model,
    });
    const response = completion.choices[0].message;
    return {
      content: response.content || "",
      role: response.role,
    };
  }
}
