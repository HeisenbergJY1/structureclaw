import type { SkillManifest } from '../../../agent-runtime/types.js';

export const manifest: SkillManifest = {
  id: 'section-common',
  domain: 'section',
  structureType: 'frame',
  name: {
    zh: '通用截面设计',
    en: 'Common Section Designer'
  },
  description: {
    zh: '常规梁、框架、柱与标准型钢截面的补参、默认建议与模型骨架生成。',
    en: 'Parameter clarification, default guidance, and model skeleton generation for common beams, frames, columns, and standard profiles.'
  },
  triggers: ['截面', '工字钢', 'H型钢', '钢框架', '型钢', 'section', 'section design', 'profile'],
  stages: ['intent', 'draft', 'analysis', 'design'],
  autoLoadByDefault: false,
  structuralTypeKeys: ['beam', 'frame', 'steel-frame', 'bridge'],
  capabilities: ['section.detect', 'section.draft', 'section.model', 'section.validate'],
  enabledTools: ['draft_model', 'update_model', 'validate_model'],
  materialFamilies: ['steel', 'composite'],
  priority: 100,
  requires: [],
  conflicts: [],
  compatibility: {
    minRuntimeVersion: '0.1.0',
    skillApiVersion: 'v1'
  }
};

export default manifest;