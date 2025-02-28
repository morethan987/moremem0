import { addMemories, retrieveMemories } from "../src";
import { LanguageModelV1Prompt } from "ai";
import { testConfig } from "../config/test-config";

describe("Memory Core Functions", () => {
  const { userId } = testConfig;
  jest.setTimeout(50000);

  describe("addMemories", () => {
    it("should successfully add memories and return correct format", async () => {
      const messages: LanguageModelV1Prompt = [
        {
          role: "user",
          content: [
            { type: "text", text: "I love red cars." },
            { type: "text", text: "I like Toyota Cars." },
            { type: "text", text: "I prefer SUVs." },
          ],
        }
      ];

      const response = await addMemories(messages, { user_id: userId });
      
      expect(response).toHaveProperty('results');
      expect(response).toHaveProperty('relations');
      expect(Array.isArray(response.results)).toBe(true);
      expect(Array.isArray(response.relations.added_triples)).toBe(true);
      
      response.results.forEach((memory: any) => {
        expect(memory).toHaveProperty('id');
        expect(memory).toHaveProperty('memory');
        expect(memory).toHaveProperty('event');
        expect(memory).toHaveProperty('categories');
        expect(Array.isArray(memory.categories)).toBe(true);
      });
    });
  });

  describe("retrieveMemories", () => {
    // beforeEach(async () => {
    //   // Add some test memories before each retrieval test
    //   const messages: LanguageModelV1Prompt = [
    //     {
    //       role: "user",
    //       content: [
    //         { type: "text", text: "I love red cars." },
    //         { type: "text", text: "I like Toyota Cars." },
    //         { type: "text", text: "I prefer SUVs." },
    //       ],
    //     }
    //   ];
    //   await addMemories(messages, { user_id: userId });
    // });

    it("should retrieve memories with string prompt", async () => {
      const prompt = "Which car would I prefer?";
      const response = await retrieveMemories(prompt, { user_id: userId });
      
      expect(typeof response).toBe('string');
      expect(response).toMatch(/Memory:/);
    });

    it("should retrieve memories with array of prompts", async () => {
      const messages: LanguageModelV1Prompt = [
        {
          role: "user",
          content: [
            { type: "text", text: "Which car would I prefer?" },
            { type: "text", text: "Suggest me some cars" },
          ],
        }
      ];

      const response = await retrieveMemories(messages, { user_id: userId });
      
      expect(typeof response).toBe('string');
      expect(response).toMatch(/Memory:/);
    });
  });
});