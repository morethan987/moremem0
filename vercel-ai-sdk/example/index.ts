import { generateText, LanguageModelV1Prompt } from 'ai';
import { createMem0, addMemories, retrieveMemories } from '../src';
import dotenv from 'dotenv';

// 这是一个不那么消耗Mem0次数的测试文件
// 使用 pnpm dev来运行这个文件
// 如果想运行别的文件，请修改nodemon.json文件

// 加载环境变量
dotenv.config();

const mem0ApiKey = process.env.MEM0_API_KEY;
const deepseekApiKey = process.env.DEEPSEEK_API_KEY;
const aliyunApiKey = process.env.ALIYUN_API_KEY;
//'deepseek-chat'
const responseModel = 'qwen-max-latest';

if (!mem0ApiKey || !aliyunApiKey) {
  console.error('请确保设置了 MEM0_API_KEY 和其他相关环境变量');
  process.exit(1);
}

// 创建Mem0实例
const mem0 = createMem0({
  provider: 'aliyun',
  mem0ApiKey,
  apiKey: aliyunApiKey,
  config: {
    compatibility: 'compatible',
  }
});

async function testMemoryFeatures() {
  try {
    // 1. 添加记忆
    console.log('添加记忆...');
    const messages: LanguageModelV1Prompt = [
      {
        role: 'user',
        content: [
          { type: 'text', text: '我喜欢红色的汽车。' },
          { type: 'text', text: '我喜欢丰田的汽车。' },
          { type: 'text', text: '我更喜欢SUV。' }
        ]
      }
    ];

    await addMemories(messages, { 
      user_id: 'test-user',
      mem0ApiKey 
    });
    console.log('记忆添加成功！');

    // 2. 检索记忆
    console.log('\n检索记忆...');
    const prompt = '推荐一辆适合我的汽车';
    const memories = await retrieveMemories(prompt, { 
      user_id: 'test-user',
      mem0ApiKey 
    });
    console.log('检索到的记忆:', memories);

    // 3. 使用记忆生成回复
    console.log('\n生成带记忆上下文的回复...');
    const { text } = await generateText({
      model: mem0(responseModel, {
        user_id: 'test-user'
      }),
      messages: [
        {
          role: 'user',
          content: [
            { type: 'text', text: '根据我的喜好推荐一辆汽车' }
          ]
        }
      ]
    });
    
    console.log('AI回复:', text);

  } catch (error) {
    console.error('错误:', error);
  }
}

// 运行测试
testMemoryFeatures();