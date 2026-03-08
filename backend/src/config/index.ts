import dotenv from 'dotenv';

dotenv.config();

const redisUrlRaw = process.env.REDIS_URL;
const redisEnabled = redisUrlRaw && redisUrlRaw.toLowerCase() !== 'disabled';

export const config = {
  // 服务配置
  port: parseInt(process.env.PORT || '8000', 10),
  host: process.env.HOST || '0.0.0.0',
  nodeEnv: process.env.NODE_ENV || 'development',

  // 数据库配置
  databaseUrl: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/structureclaw',

  // Redis 配置
  redisUrl: redisEnabled ? redisUrlRaw! : '',

  // JWT 配置
  jwtSecret: process.env.JWT_SECRET || 'your-super-secret-jwt-key',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '7d',

  // AI 配置
  openaiApiKey: process.env.OPENAI_API_KEY || '',
  openaiModel: process.env.OPENAI_MODEL || 'gpt-4-turbo-preview',
  openaiBaseUrl: process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1',

  // 分析引擎配置
  analysisEngineUrl: process.env.ANALYSIS_ENGINE_URL || 'http://localhost:8001',

  // CORS
  corsOrigins: (process.env.CORS_ORIGINS || 'http://localhost:3000').split(','),

  // 文件存储
  uploadDir: process.env.UPLOAD_DIR || './uploads',
  maxFileSize: parseInt(process.env.MAX_FILE_SIZE || '104857600', 10), // 100MB

  // 日志级别
  logLevel: process.env.LOG_LEVEL || 'info',
};

export type Config = typeof config;
