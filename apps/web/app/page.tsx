'use client';
import dynamic from 'next/dynamic';
const Studio=dynamic(()=>import('@/components/Studio'),{ssr:false,loading:()=> <div className="boot"><span className="brand-mark">SF</span><p>Preparing the foundry…</p></div>});
export default function Page(){return <Studio/>}
