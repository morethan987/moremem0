import { createOpenAI, OpenAIProviderSettings } from "@ai-sdk/openai";
import { generateText as aiGenerateText, streamText as aiStreamText, LanguageModelV1Prompt } from "ai";
import { updateMemories, retrieveMemories, flattenPrompt, convertMessagesToMem0Format } from "./mem0-utils";
import { Mem0Config } from "./mem0-chat-settings";
import { Mem0ProviderSettings } from "./mem0-provider";
import { CohereProviderSettings, createCohere } from "@ai-sdk/cohere";
import { AnthropicProviderSettings, createAnthropic } from "@ai-sdk/anthropic";
import { createGroq, GroqProviderSettings } from "@ai-sdk/groq";
import { createDeepSeek, DeepSeekProviderSettings } from "@ai-sdk/deepseek";
import { createOpenAICompatible, OpenAICompatibleProviderSettings} from "@ai-sdk/openai-compatible"

export type Provider = ReturnType<typeof createOpenAI> | ReturnType<typeof createCohere> | ReturnType<typeof createAnthropic> | ReturnType<typeof createGroq> | ReturnType<typeof createDeepSeek> | any;
export type ProviderSettings = OpenAIProviderSettings | CohereProviderSettings | AnthropicProviderSettings | GroqProviderSettings | DeepSeekProviderSettings | OpenAICompatibleProviderSettings;

class Mem0AITextGenerator {
    provider: Provider;
    model: string;
    provider_config?: ProviderSettings;
    config: Mem0ProviderSettings;

    constructor(provider: string, model: string, config: Mem0ProviderSettings, provider_config: ProviderSettings) {
        switch (provider) {
            case "openai":
                this.provider = createOpenAI({
                    apiKey: config?.apiKey,
                    ...provider_config,
                });
                if(config?.modelType === "completion"){
                    this.provider = createOpenAI({
                        apiKey: config?.apiKey,
                        ...provider_config,
                    }).completion;
                }else if(config?.modelType === "chat"){
                    this.provider = createOpenAI({
                        apiKey: config?.apiKey,
                        ...provider_config,
                    }).chat;
                }
                break;
            case "cohere":
                this.provider = createCohere({
                    apiKey: config?.apiKey,
                    ...provider_config,
                });
                break;
            case "anthropic":
                this.provider = createAnthropic({
                    apiKey: config?.apiKey,
                    ...provider_config,
                });
                break;
            case "groq":
                this.provider = createGroq({
                    apiKey: config?.apiKey,
                    ...provider_config,
                });
                break;
            case "deepseek":
                this.provider = createDeepSeek({
                    apiKey: config?.apiKey,
                    ...provider_config,
                });
                break;
            case "aliyun":
                this.provider = createOpenAICompatible({
                    apiKey: config?.apiKey,
                    baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    name: 'aliyun',
                    ...provider_config,
                });
                break;
            default:
                throw new Error("Unsupported provider");
        }
        this.model = model;
        this.provider_config = provider_config;
        this.config = config!;
    }
    

    async generateText(prompt: LanguageModelV1Prompt, config: Mem0Config) {
        try {
            const flattenPromptResponse = flattenPrompt(prompt);
            const newPrompt = await retrieveMemories(prompt, config);
            const response = await aiGenerateText({
                // @ts-ignore
                model: this.provider(this.model),
                messages: prompt,
                system: newPrompt
            });

            const mem0Prompts = convertMessagesToMem0Format(prompt);

            await updateMemories(mem0Prompts as any, config);

            return response;
        } catch (error) {
            console.error("Error generating text:", error);
            throw error;
        }
    }

    async streamText(prompt: LanguageModelV1Prompt, config: Mem0Config) {
        try {
            const flattenPromptResponse = flattenPrompt(prompt);
            const newPrompt = await retrieveMemories(prompt, config);
            console.log("newPrompt", newPrompt);

            await updateMemories([
                { role: "user", content: flattenPromptResponse },
                { role: "assistant", content: "Thank You!" },
            ], config);

            const response = await aiStreamText({
                // @ts-ignore
                model: this.provider(this.model),
                messages: prompt,
                system: newPrompt
            });
          
            return response;
        } catch (error) {
            console.error("Error generating text:", error);
            throw error;
        }
    }
}

export default Mem0AITextGenerator;
