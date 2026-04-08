import type { SkillManifest } from '../../../agent-runtime/types.js';

export const manifest: SkillManifest = {
  id: 'section-irregular',
  domain: 'section',
  structureType: 'unknown',
  name: {
    zh: '异形与变截面设计',
    en: 'Irregular Section Designer',
  },
  description: {
    zh: '变截面、异形、开孔、偏心与自定义轮廓截面的补参、默认建议与轮廓骨架生成。',
    en: 'Parameter clarification, default guidance, and outline-skeleton generation for tapered, asymmetric, perforated, and custom sections.',
  },
  triggers: ['不规则', '变截面', '异形', '开孔', 'tapered', 'haunch', 'asymmetric', 'custom', 'polygon', 'outline', '自定义'],
  stages: ['intent', 'draft', 'analysis', 'design'],
  autoLoadByDefault: false,
  structuralTypeKeys: ['unknown', 'beam', 'frame', 'bridge'],
  capabilities: ['section.detect', 'section.irregular-model', 'section.outline', 'section.validate'],
  enabledTools: ['draft_model', 'update_model', 'validate_model'],
  materialFamilies: ['steel', 'concrete', 'composite', 'timber'],
  priority: 140,
  requires: [],
  conflicts: [],
  compatibility: {
    minRuntimeVersion: '0.1.0',
    skillApiVersion: 'v1',
  },
};

export default manifest;
