export const metadata = {
    title: "Términos y Condiciones",
    description: "Términos y condiciones del consultorio de la Dra. Lina María Valencia Arias.",
};

export default function TerminosPage() {
    return (
        <div className="pt-20 pb-12 md:pt-24 md:pb-16">
            <div className="max-w-3xl mx-auto px-6">
                <h1 className="text-3xl font-bold text-slate-900">
                    Términos y Condiciones
                </h1>
                <div className="mt-3 w-16 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full" />

                <div className="mt-8 space-y-6 text-slate-600 leading-relaxed">
                    <section>
                        <h2 className="text-xl font-bold text-slate-900 mb-3">
                            1. Información General
                        </h2>
                        <p>
                            Este sitio web es operado por el consultorio médico de la
                            Dra. Lina María Valencia Arias, ubicado en Rovira, Tolima, Colombia.
                            Al utilizar este sitio web, usted acepta cumplir con estos términos
                            y condiciones.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-slate-900 mb-3">
                            2. Servicios Médicos
                        </h2>
                        <p>
                            La información proporcionada en este sitio web tiene fines
                            informativos y no sustituye la consulta médica profesional. Las
                            citas agendadas a través de este sitio están sujetas a disponibilidad
                            y confirmación.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-slate-900 mb-3">
                            3. Protección de Datos
                        </h2>
                        <p>
                            Sus datos personales serán tratados conforme a la Ley 1581 de 2012
                            de Protección de Datos Personales de Colombia. La información
                            proporcionada al agendar citas se utilizará exclusivamente para la
                            prestación de servicios médicos.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-slate-900 mb-3">
                            4. Cancelación de Citas
                        </h2>
                        <p>
                            Las citas pueden ser canceladas o reprogramadas con al menos 24
                            horas de anticipación. Las cancelaciones tardías o inasistencias pueden
                            afectar la disponibilidad futura de citas.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-slate-900 mb-3">
                            5. Contacto
                        </h2>
                        <p>
                            Para cualquier consulta sobre estos términos, puede comunicarse
                            directamente con el consultorio.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    );
}
