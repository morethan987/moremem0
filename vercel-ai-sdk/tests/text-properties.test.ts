import { generateText, streamText } from "ai";
import { testConfig } from "../config/test-config";

interface Provider {
  name: string;
  activeModel: string;
  apiKey: string | undefined;
}

describe.each(testConfig.providers)('TEXT/STREAM PROPERTIES: Tests with model %s', (provider: Provider) => {
  const { userId } = testConfig;
  let mem0: ReturnType<typeof testConfig.createTestClient>;
  jest.setTimeout(50000);

  beforeEach(() => {
    mem0 = testConfig.createTestClient(provider);
  });

  it("should stream text with onChunk handler", async () => {
    const chunkTexts: string[] = [];
    const { textStream } = await streamText({
      model: mem0(provider.activeModel, {
        user_id: userId, // Use the uniform userId
      }),
      prompt: "Write only the name of the car I prefer and its color.",
      onChunk({ chunk }) {
        if (chunk.type === "text-delta") {
          // Store chunk text for assertions
          chunkTexts.push(chunk.textDelta);
        }
      },
    });

    // Wait for the stream to complete
    for await (const _ of textStream) {
    }

    // Ensure chunks are collected
    expect(chunkTexts.length).toBeGreaterThan(0);
    expect(chunkTexts.every((text) => typeof text === "string")).toBe(true);
  });

  it("should call onFinish handler without throwing an error", async () => {
    await streamText({
      model: mem0(provider.activeModel, {
        user_id: userId, // Use the uniform userId
      }),
      prompt: "Write only the name of the car I prefer and its color.",
      onFinish({ text, finishReason, usage }) {

      },
    });
  });

  it("should generate fullStream with expected usage", async () => {
    const {
      text, // combined text
      usage, // combined usage of all steps
    } = await generateText({
      model: mem0(provider.activeModel), // Ensure the model name is correct
      maxSteps: 5, // Enable multi-step calls
      experimental_continueSteps: true,
      prompt:
        "Suggest me some good cars to buy. Each response MUST HAVE at least 200 words.",
    });

    // Ensure text is a string
    expect(typeof text).toBe("string");

    // Check usage
    // promptTokens is a number, so we use toBeCloseTo instead of toBe and it should be in the range 155 to 165
    expect(usage.promptTokens).toBeGreaterThanOrEqual(10);
    expect(usage.promptTokens).toBeLessThanOrEqual(5000);
    expect(usage.completionTokens).toBeGreaterThanOrEqual(10); // Lowered threshold for completion tokens
    expect(usage.totalTokens).toBeGreaterThan(20); // Lowered threshold for total tokens
  });
});
