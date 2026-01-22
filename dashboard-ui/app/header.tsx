import Image from 'next/image';

export default function Header() {
  return (
    <header className="bg-slate-50 shadow-sm w-full mb-4 content-center">
      <div className="px-6 py-4 flex flex-row">
        <Image
          src="/CHTC_Logo_Full_Color.svg"
          alt="CHTC Logo"
          width={120}
          height={40}
          priority
        />
        <h1 className="text-3xl font-semibold leading-10 tracking-tight text-black pl-2">
          Personal AP Dashboard
        </h1>
      </div>
    </header>
  );
}
