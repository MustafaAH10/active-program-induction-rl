import type { Metadata } from 'next';
import './globals.css';
export const metadata:Metadata={title:'SkyFoundry — Agentic construction studio',description:'A deterministic 3D architectural concept simulator.',icons:{icon:'/icon.svg'}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
