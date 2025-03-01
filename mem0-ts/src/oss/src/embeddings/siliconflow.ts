import OpenAI from "openai";
import { Embedder } from "./base";
import { EmbeddingConfig } from "../types";

interface EmbeddingData {
  object: "embedding";
  embedding: number[];
  index: number;
}

interface SiliconFlowEmbeddingResponse {
  model: string;
  data: EmbeddingData[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

interface SiliconFlowErrorResponse {
  error: string;
  message?: string;
}

interface RequestOptions {
  input: string | string[];
  model: string;
  encoding_format: "float";
}

class SiliconFlow {
  protected apiKey: string;
  protected model: string;
  private baseUrl = 'https://api.siliconflow.cn/v1';

  constructor(config: EmbeddingConfig) {
    this.apiKey = config.apiKey;
    this.model = config.model || "Pro/BAAI/bge-m3";
  }

  protected async makeRequest<T>(endpoint: string, options: RequestOptions): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(options)
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: response.statusText })) as SiliconFlowErrorResponse;
      throw new Error(`SiliconFlow API error: ${error.error || 'Unknown error'}`);
    }

    const result = await response.json();
    return result as T;
  }
}

export class SiliconFlowEmbedder extends SiliconFlow implements Embedder {
  constructor(config: EmbeddingConfig) {
    super(config);
  }

  async embed(text: string): Promise<number[]> {
    const result = await this.makeRequest<SiliconFlowEmbeddingResponse>('/embeddings', {
      input: text,
      model: this.model,
      encoding_format: "float"
    });

    if (!result.data?.[0]?.embedding) {
      throw new Error('Invalid response format from SiliconFlow API');
    }
    return result.data[0].embedding;
  }

  async embedBatch(texts: string[]): Promise<number[][]> {
    const result = await this.makeRequest<SiliconFlowEmbeddingResponse>('/embeddings', {
      input: texts,
      model: this.model,
      encoding_format: "float"
    });

    if (!result.data?.[0]?.embedding) {
      throw new Error('Invalid response format from SiliconFlow API');
    }
    return result.data.map(item => item.embedding);
  }
}
