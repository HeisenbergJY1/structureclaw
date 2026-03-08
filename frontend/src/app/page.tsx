import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800">
      {/* Header */}
      <header className="border-b border-slate-700">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <span className="text-white text-xl font-bold">StructureClaw</span>
          </div>
          <nav className="flex items-center gap-6">
            <Link href="/docs" className="text-slate-300 hover:text-white transition">
              文档
            </Link>
            <Link href="/community" className="text-slate-300 hover:text-white transition">
              社区
            </Link>
            <Link href="/skills" className="text-slate-300 hover:text-white transition">
              技能市场
            </Link>
            <Button variant="default">登录</Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-white mb-6">
          智能建筑结构分析设计平台
        </h1>
        <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
          融合 AI 智能助手、有限元分析引擎和协作社区，为结构工程师打造下一代设计工具
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" className="bg-blue-500 hover:bg-blue-600">
            开始使用
          </Button>
          <Button size="lg" variant="outline" className="border-slate-600 text-white">
            查看演示
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">AI 结构助手</CardTitle>
              <CardDescription className="text-slate-400">
                基于大语言模型的智能顾问，解答结构分析问题
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-slate-300 space-y-2 text-sm">
                <li>• 结构建模咨询</li>
                <li>• 荷载计算指导</li>
                <li>• 规范条文解读</li>
                <li>• 设计优化建议</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">有限元分析</CardTitle>
              <CardDescription className="text-slate-400">
                基于 OpenSees 的专业分析引擎
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-slate-300 space-y-2 text-sm">
                <li>• 静力分析</li>
                <li>• 模态分析</li>
                <li>• 地震响应分析</li>
                <li>• 非线性 Pushover</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">技能市场</CardTitle>
              <CardDescription className="text-slate-400">
                丰富的结构工程工具和技能
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-slate-300 space-y-2 text-sm">
                <li>• 截面设计工具</li>
                <li>• 荷载计算器</li>
                <li>• 规范校核</li>
                <li>• 计算书生成</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold text-blue-400 mb-2">1000+</div>
            <div className="text-slate-400">注册用户</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-green-400 mb-2">50+</div>
            <div className="text-slate-400">分析技能</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-purple-400 mb-2">10000+</div>
            <div className="text-slate-400">分析任务</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-orange-400 mb-2">99.9%</div>
            <div className="text-slate-400">服务可用性</div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 py-8">
        <div className="container mx-auto px-4 text-center text-slate-400">
          <p>&copy; 2024 StructureClaw. 开源项目，基于 MIT 许可证</p>
          <div className="flex justify-center gap-6 mt-4">
            <Link href="/docs" className="hover:text-white">文档</Link>
            <Link href="https://github.com" className="hover:text-white">GitHub</Link>
            <Link href="/community" className="hover:text-white">社区</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
