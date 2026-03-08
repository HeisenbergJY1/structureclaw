import type { Prisma } from '@prisma/client';
import { prisma } from '../utils/database.js';
import { ensureUserId } from '../utils/demo-data.js';

interface ListPostsParams {
  category?: string;
  tag?: string;
  sort?: string;
  page?: number;
  limit?: number;
}

interface CreatePostParams {
  title: string;
  content: string;
  category: string;
  tags: string[];
  attachments?: string[];
  projectId?: string;
  authorId?: string;
}

interface CreateCommentParams {
  postId: string;
  content: string;
  parentId?: string;
  authorId?: string;
}

export class CommunityService {
  async listPosts(params: ListPostsParams = {}) {
    const where: Record<string, unknown> = {};

    if (params.category) {
      where.category = params.category;
    }

    if (params.tag) {
      where.tags = { has: params.tag };
    }

    const orderBy: Prisma.PostOrderByWithRelationInput[] =
      params.sort === 'popular'
        ? [{ likeCount: 'desc' }, { viewCount: 'desc' }]
        : [{ createdAt: 'desc' }];

    return prisma.post.findMany({
      where,
      include: {
        author: {
          select: {
            id: true,
            name: true,
            avatar: true,
          },
        },
        _count: {
          select: {
            comments: true,
            likes: true,
          },
        },
      },
      orderBy,
      skip: ((params.page || 1) - 1) * (params.limit || 20),
      take: params.limit || 20,
    });
  }

  async createPost(params: CreatePostParams) {
    const authorId = await ensureUserId(params.authorId);

    return prisma.post.create({
      data: {
        title: params.title,
        content: params.content,
        category: params.category,
        tags: params.tags,
        attachments: params.attachments || [],
        projectId: params.projectId,
        authorId,
      },
    });
  }

  async getPost(id: string) {
    await prisma.post.update({
      where: { id },
      data: {
        viewCount: {
          increment: 1,
        },
      },
    }).catch(() => undefined);

    return prisma.post.findUnique({
      where: { id },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            avatar: true,
            organization: true,
          },
        },
        comments: {
          where: { parentId: null },
          include: {
            author: {
              select: {
                id: true,
                name: true,
                avatar: true,
              },
            },
            replies: true,
          },
          orderBy: { createdAt: 'asc' },
        },
      },
    });
  }

  async likePost(id: string, userId?: string) {
    const resolvedUserId = await ensureUserId(userId);
    const existingLike = await prisma.postLike.findFirst({
      where: {
        postId: id,
        userId: resolvedUserId,
      },
    });

    if (existingLike) {
      return { success: true, liked: true };
    }

    await prisma.postLike.create({
      data: {
        postId: id,
        userId: resolvedUserId,
      },
    });

    await prisma.post.update({
      where: { id },
      data: {
        likeCount: {
          increment: 1,
        },
      },
    });

    return { success: true, liked: true };
  }

  async getComments(postId: string) {
    return prisma.comment.findMany({
      where: { postId },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            avatar: true,
          },
        },
      },
      orderBy: { createdAt: 'asc' },
    });
  }

  async createComment(params: CreateCommentParams) {
    const authorId = await ensureUserId(params.authorId);

    return prisma.comment.create({
      data: {
        postId: params.postId,
        content: params.content,
        parentId: params.parentId,
        authorId,
      },
    });
  }

  async listKnowledge(category?: string) {
    return prisma.post.findMany({
      where: {
        category: category || {
          in: ['tutorial', 'case-study'],
        },
      },
      orderBy: { createdAt: 'desc' },
      take: 50,
    });
  }

  async getPopularTags() {
    const posts = await prisma.post.findMany({
      select: { tags: true },
      take: 100,
      orderBy: { createdAt: 'desc' },
    });

    const counts = new Map<string, number>();
    for (const post of posts) {
      for (const tag of post.tags) {
        counts.set(tag, (counts.get(tag) || 0) + 1);
      }
    }

    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 20)
      .map(([tag, count]) => ({ tag, count }));
  }

  async search(q: string, type?: string) {
    if (type === 'skills') {
      const skills = await prisma.skill.findMany({
        where: {
          OR: [
            { name: { contains: q, mode: 'insensitive' } },
            { description: { contains: q, mode: 'insensitive' } },
          ],
        },
        take: 20,
      });

      return { posts: [], skills };
    }

    const [posts, skills] = await Promise.all([
      prisma.post.findMany({
        where: {
          OR: [
            { title: { contains: q, mode: 'insensitive' } },
            { content: { contains: q, mode: 'insensitive' } },
            { tags: { has: q } },
          ],
        },
        take: 20,
        orderBy: { createdAt: 'desc' },
      }),
      prisma.skill.findMany({
        where: {
          OR: [
            { name: { contains: q, mode: 'insensitive' } },
            { description: { contains: q, mode: 'insensitive' } },
          ],
        },
        take: 20,
      }),
    ]);

    return { posts, skills };
  }
}
