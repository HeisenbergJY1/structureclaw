import { ChatOpenAI } from '@langchain/openai';
import { ConversationChain } from 'langchain/chains';
import { BufferMemory } from 'langchain/memory';
import { PromptTemplate } from '@langchain/core/prompts';
import { config } from '../config/index.js';
import { prisma } from '../utils/database.js';

// 结构工程专用提示词
const STRUCTURAL_ENGINEER_SYSTEM_PROMPT = `你是一位专业的建筑结构工程师和顾问，专注于结构分析、设计和规范解读。

你的专业领域包括：
1. 结构分析方法：静力分析、动力分析、非线性分析、稳定性分析
2. 结构设计：混凝土结构、钢结构、组合结构、砌体结构
3. 规范解读：中国规范（GB系列）、国际规范
4. 地震工程：抗震设计、动力时程分析、Pushover分析
5. 荷载计算：恒载、活载、风荷载、地震作用
6. 有限元分析：建模技巧、网格划分、边界条件设置

回答问题时请：
- 使用专业的结构工程术语
- 提供具体的计算公式和方法
- 引用相关规范条文
- 给出实用建议和注意事项
- 如需进一步信息，主动询问

当前对话上下文：
{chat_history}

用户问题：{input}

请提供专业、准确、实用的回答：`;

export interface SendMessageParams {
  message: string;
  conversationId?: string;
  userId?: string;
  context?: {
    projectId?: string;
    analysisType?: string;
  };
}

export interface StreamChunk {
  type: 'token' | 'done' | 'error';
  content?: string;
  error?: string;
}

export class ChatService {
  private llm: ChatOpenAI | null;
  private memories: Map<string, BufferMemory>;

  constructor() {
    this.llm = config.openaiApiKey
      ? new ChatOpenAI({
          modelName: config.openaiModel,
          temperature: 0.3,
          openAIApiKey: config.openaiApiKey,
          configuration: {
            baseURL: config.openaiBaseUrl,
          },
        })
      : null;
    this.memories = new Map();
  }

  async sendMessage(params: SendMessageParams) {
    const { message, conversationId, userId, context } = params;

    // 获取或创建会话
    let conversation;
    if (conversationId) {
      conversation = await prisma.conversation.findUnique({
        where: { id: conversationId },
        include: { messages: { orderBy: { createdAt: 'asc' } } },
      });
    } else {
      conversation = await prisma.conversation.create({
        data: {
          title: message.slice(0, 50),
          type: 'general',
          userId,
        },
        include: { messages: true },
      });
    }

    if (!conversation) {
      throw new Error('会话不存在');
    }

    // 获取记忆
    const memory = this.getMemory(conversation.id);

    // 构建上下文
    const projectContext = context?.projectId
      ? await this.getProjectContext(context.projectId)
      : '';

    if (!this.llm) {
      const fallbackResponse = 'AI 聊天功能未配置 `OPENAI_API_KEY`，其余 API 服务可正常使用。';

      await prisma.message.createMany({
        data: [
          {
            conversationId: conversation.id,
            role: 'user',
            content: message,
          },
          {
            conversationId: conversation.id,
            role: 'assistant',
            content: fallbackResponse,
          },
        ],
      });

      return {
        conversationId: conversation.id,
        response: fallbackResponse,
      };
    }

    // 创建对话链
    const prompt = PromptTemplate.fromTemplate(STRUCTURAL_ENGINEER_SYSTEM_PROMPT);
    const chain = new ConversationChain({
      llm: this.llm,
      memory,
      prompt,
    });

    // 发送消息并获取响应
    const response = await chain.invoke({
      input: projectContext ? `[项目上下文]\n${projectContext}\n\n[用户问题]\n${message}` : message,
    });

    // 保存消息
    await prisma.message.createMany({
      data: [
        {
          conversationId: conversation.id,
          role: 'user',
          content: message,
        },
        {
          conversationId: conversation.id,
          role: 'assistant',
          content: response.response,
        },
      ],
    });

    return {
      conversationId: conversation.id,
      response: response.response,
    };
  }

  async *streamMessage(params: SendMessageParams): AsyncGenerator<StreamChunk> {
    const { message, conversationId, userId } = params;

    try {
      // 获取或创建会话
      let conversation;
      if (conversationId) {
        conversation = await prisma.conversation.findUnique({
          where: { id: conversationId },
        });
      } else {
        conversation = await prisma.conversation.create({
          data: {
            title: message.slice(0, 50),
            type: 'general',
            userId,
          },
        });
      }

      if (!conversation) {
        throw new Error('会话不存在');
      }

      if (!this.llm) {
        const fallbackResponse = 'AI 聊天功能未配置 `OPENAI_API_KEY`，其余 API 服务可正常使用。';

        await prisma.message.createMany({
          data: [
            {
              conversationId: conversation.id,
              role: 'user',
              content: message,
            },
            {
              conversationId: conversation.id,
              role: 'assistant',
              content: fallbackResponse,
            },
          ],
        });

        yield { type: 'token', content: fallbackResponse };
        yield { type: 'done' };
        return;
      }

      // 使用流式 API
      const stream = await this.llm.stream(message);
      let fullResponse = '';

      for await (const chunk of stream) {
        const token = typeof chunk.content === 'string'
          ? chunk.content
          : JSON.stringify(chunk.content);
        fullResponse += token;
        yield { type: 'token', content: token };
      }

      // 保存消息
      await prisma.message.createMany({
        data: [
          {
            conversationId: conversation.id,
            role: 'user',
            content: message,
          },
          {
            conversationId: conversation.id,
            role: 'assistant',
            content: fullResponse,
          },
        ],
      });

      yield { type: 'done' };
    } catch (error: any) {
      yield { type: 'error', error: error.message };
    }
  }

  async createConversation(params: { title?: string; type: string; userId?: string }) {
    return prisma.conversation.create({
      data: {
        title: params.title || '新对话',
        type: params.type,
        userId: params.userId,
      },
    });
  }

  async getConversation(id: string, userId?: string) {
    return prisma.conversation.findFirst({
      where: { id, userId },
      include: {
        messages: {
          orderBy: { createdAt: 'asc' },
        },
      },
    });
  }

  async getUserConversations(userId?: string) {
    return prisma.conversation.findMany({
      where: { userId },
      orderBy: { updatedAt: 'desc' },
      take: 50,
    });
  }

  private getMemory(conversationId: string): BufferMemory {
    if (!this.memories.has(conversationId)) {
      this.memories.set(
        conversationId,
        new BufferMemory({
          returnMessages: true,
          memoryKey: 'chat_history',
        })
      );
    }
    return this.memories.get(conversationId)!;
  }

  private async getProjectContext(projectId: string): Promise<string> {
    const project = await prisma.project.findUnique({
      where: { id: projectId },
      include: {
        models: {
          include: {
            analyses: {
              take: 5,
              orderBy: { createdAt: 'desc' },
            },
          },
        },
      },
    });

    if (!project) return '';

    const analysisCount = project.models.reduce((count: number, model: { analyses: unknown[] }) => {
      return count + model.analyses.length;
    }, 0);

    const projectSettings = (project.settings || {}) as { designCode?: string };

    return `
项目名称: ${project.name}
项目类型: ${project.type}
设计规范: ${projectSettings.designCode || '未指定'}
模型数量: ${project.models?.length || 0}
分析任务: ${analysisCount}
    `.trim();
  }
}
