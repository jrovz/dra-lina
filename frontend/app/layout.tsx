import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import Header from "@/components/public/Header";
import Footer from "@/components/public/Footer";
import { QueryProvider } from "@/components/QueryProvider";

const outfit = Outfit({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: {
    default: "Dra. Lina - Especialista en Salud Familiar",
    template: "%s | Dra. Lina",
  },
  description:
    "Medicina y Ecografía Clínica para la familia en Rovira, Tolima. Consulta médica general y estudios ecográficos con la Dra. Lina María Valencia Arias.",
  openGraph: {
    type: "website",
    locale: "es_CO",
    siteName: "Dra. Lina",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={outfit.className}>
        <QueryProvider>
          <Header />
          <main className="min-h-screen">{children}</main>
          <Footer />
        </QueryProvider>
      </body>
    </html>
  );
}
