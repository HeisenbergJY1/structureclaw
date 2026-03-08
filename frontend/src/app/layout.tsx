import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'StructureClaw - 建筑结构分析设计社区',
  description: '开源建筑结构分析与设计社区平台，融合 AI 智能助手、有限元分析引擎和协作社区功能',
  keywords: ['结构分析', '有限元', '建筑结构', '结构设计', 'AI', 'OpenSees'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
