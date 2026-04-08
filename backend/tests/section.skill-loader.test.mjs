import { describe, expect, test } from '@jest/globals';
import { AgentSkillLoader } from '../dist/agent-runtime/loader.js';

describe('section skill loader', () => {
  test('should discover modular section bundles', () => {
    const loader = new AgentSkillLoader();
    const bundles = loader.loadBundles();
    const ids = bundles.map((bundle) => bundle.id);

    expect(ids).toEqual(expect.arrayContaining([
      'section-common',
      'section-bridge',
      'section-irregular',
    ]));
    expect(ids).not.toContain('section');
  });

  test('should load modular section plugins and keep legacy root plugin removed', async () => {
    const loader = new AgentSkillLoader();
    const plugins = await loader.loadPlugins();
    const pluginIds = plugins.map((plugin) => plugin.id);

    expect(pluginIds).toEqual(expect.arrayContaining([
      'section-common',
      'section-bridge',
      'section-irregular',
    ]));
    expect(pluginIds).not.toContain('section');

    const common = plugins.find((plugin) => plugin.id === 'section-common');
    const bridge = plugins.find((plugin) => plugin.id === 'section-bridge');
    const irregular = plugins.find((plugin) => plugin.id === 'section-irregular');

    expect(common?.manifest.domain).toBe('section');
    expect(bridge?.manifest.domain).toBe('section');
    expect(irregular?.manifest.domain).toBe('section');
    expect(common?.manifest.autoLoadByDefault).toBe(false);
    expect(bridge?.manifest.autoLoadByDefault).toBe(false);
    expect(irregular?.manifest.autoLoadByDefault).toBe(false);
  });
});
