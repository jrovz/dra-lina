import Link from "next/link";
import { fetchDoctors, fetchServices } from "@/lib/api";
import DoctorCard from "@/components/public/DoctorCard";
import ServiceCard from "@/components/public/ServiceCard";
import type { Doctor, Service } from "@/lib/types";
import { BackgroundOrbs } from "@/components/animations/BackgroundOrbs";
import { AnimatedSection, StaggerContainer, StaggerItem } from "@/components/animations/AnimatedSection";

export default async function HomePage() {
  let doctors: Doctor[] = [];
  let services: Service[] = [];

  try {
    const [docRes, svcRes] = await Promise.all([
      fetchDoctors(),
      fetchServices(),
    ]);
    doctors = docRes.data;
    services = svcRes.data;
  } catch {
    /* API not available during build — render with empty data */
  }

  return (
    <>
      {/* Hero */}
      <section className="relative pt-20 pb-12 md:pt-24 md:pb-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-violet-50" />
        <BackgroundOrbs /> {/* Premium moving orbs */}

        <div className="relative max-w-6xl mx-auto px-6 text-center pt-16">
          <AnimatedSection delay={0.1}>
            <h1 className="text-4xl md:text-6xl font-extrabold text-slate-900 leading-tight tracking-tight">
              Medicina y Ecografía
              <br />
              <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
                Clínica para la Familia
              </span>
            </h1>
          </AnimatedSection>

          <AnimatedSection delay={0.3} direction="up">
            <p className="mt-6 text-lg text-slate-500 max-w-2xl mx-auto leading-relaxed">
              Atención médica integral con tecnología ecográfica de vanguardia.
              Más de 25 años cuidando la salud de familias en Rovira, Tolima.
            </p>
          </AnimatedSection>

          <AnimatedSection delay={0.5} direction="up" className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/reservar"
              className="px-8 py-3.5 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold text-base shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 hover:-translate-y-0.5 transition-all duration-300"
            >
              Agendar Cita
            </Link>
            <Link
              href="/blog"
              className="px-8 py-3.5 rounded-full border-2 border-slate-200 text-slate-700 font-semibold text-base hover:border-indigo-300 hover:text-indigo-600 transition-all duration-300"
            >
              Blog de Salud
            </Link>
          </AnimatedSection>
        </div>
      </section>

      {/* Historia */}
      <section className="relative py-12 md:py-20 bg-white overflow-hidden">
        <AnimatedSection className="max-w-4xl mx-auto px-6 relative z-10">
          <h2 className="text-3xl font-bold text-slate-900 text-center">
            Mi Historia
          </h2>
          <div className="mt-3 w-16 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto" />

          <StaggerContainer className="mt-10 space-y-5 text-slate-600 leading-relaxed">
            <StaggerItem>
              <p>Hola! Yo soy <strong className="text-slate-800">Lina María Valencia Arias</strong>, nací en Pereira en 1972, me gradué como
                Médico y Cirujano en la Universidad Tecnológica de Pereira en 1996, hice mi año de Servicio Social
                Obligatorio en Mistrató Risaralda. Después de casarme, con mi esposo y nuestros hijos nos radicamos
                en Rovira Tolima, un municipio a una hora de Ibagué. He trabajado en el Hospital de Rovira, como
                médico general.</p>
            </StaggerItem>
            <StaggerItem>
              <p>En 2005 me gradué de la Especialización en Gerencia de Servicios de Salud, en la Universidad
                Cooperativa de Colombia, sede Ibagué.</p>
            </StaggerItem>
            <StaggerItem>
              <p>En 2009 me gradué de la Especialización en Salud Familiar de la Fundación Universitaria del Área
                Andina en Bogotá, donde aprendí el uso de la Ecografía como herramienta fundamental en la Atención
                Primaria en Salud.</p>
            </StaggerItem>
            <StaggerItem>
              <p>Estuve encargada por más de 12 años de la atención de las gestantes del Hospital San Vicente de
                Rovira Tolima (Control Prenatal y Ecografías).</p>
            </StaggerItem>
            <StaggerItem>
              <p>En los años 2024 y 2025 trabajé primero como médico de un equipo básico de salud y luego como
                coordinadora de los equipos básicos del municipio sin dejar mi práctica particular.</p>
            </StaggerItem>
            <StaggerItem>
              <p>Actualmente me dedico a la práctica particular en mi consultorio, en Rovira, donde atiendo consulta
                médica y realizo estudios de <strong className="text-slate-800">Ecografía Clínica</strong>.</p>
            </StaggerItem>
            <StaggerItem>
              <p>Soy esposa, madre de tres hijos, de 28, 26 y 20 años, y una convencida de que las tecnologías como el
                ultrasonido son el presente y futuro de la medicina.</p>
            </StaggerItem>
            <StaggerItem>
              <p>Me gusta estar actualizada, en el momento estoy cursando un <strong className="text-slate-800">Grand Máster en Ecografía
                Clínica</strong>, para poder brindar cada vez un mejor servicio.</p>
            </StaggerItem>
          </StaggerContainer>
        </AnimatedSection>
      </section>

      {/* Servicios */}
      {services.length > 0 && (
        <section className="py-12 md:py-20 bg-slate-50 relative overflow-hidden">
          <div className="max-w-6xl mx-auto px-6 relative z-10">
            <AnimatedSection>
              <h2 className="text-3xl font-bold text-slate-900 text-center">
                Nuestros Servicios
              </h2>
              <div className="mt-3 w-16 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto" />
            </AnimatedSection>

            <StaggerContainer className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {services.map((svc) => (
                <StaggerItem key={svc.id}>
                  <ServiceCard service={svc} />
                </StaggerItem>
              ))}
            </StaggerContainer>
          </div>
        </section>
      )}

      {/* Doctores */}
      {doctors.length > 0 && (
        <section className="py-12 md:py-20 bg-white">
          <div className="max-w-6xl mx-auto px-6">
            <AnimatedSection>
              <h2 className="text-3xl font-bold text-slate-900 text-center">
                Nuestra Especialista
              </h2>
              <div className="mt-3 w-16 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto" />
            </AnimatedSection>

            <StaggerContainer className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {doctors.map((doc) => (
                <StaggerItem key={doc.id}>
                  <DoctorCard doctor={doc} />
                </StaggerItem>
              ))}
            </StaggerContainer>
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="py-12 md:py-20 bg-gradient-to-br from-indigo-600 to-violet-700 relative overflow-hidden">
        {/* Abstract CTA decoration */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white opacity-5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-indigo-300 opacity-20 rounded-full blur-2xl" />

        <AnimatedSection className="max-w-3xl mx-auto px-6 text-center relative z-10">
          <h2 className="text-3xl font-bold text-white">
            ¿Necesitas una consulta?
          </h2>
          <p className="mt-4 text-indigo-100 text-lg">
            Agenda tu cita de forma rápida y sencilla. Estamos aquí para
            cuidar de tu salud.
          </p>
          <Link
            href="/reservar"
            className="mt-8 inline-block px-10 py-4 rounded-full bg-white text-indigo-700 font-bold text-lg shadow-xl hover:shadow-2xl hover:-translate-y-0.5 transition-all duration-300"
          >
            Reservar Ahora
          </Link>
        </AnimatedSection>
      </section>
    </>
  );
}
