import BookingWizard from "@/components/public/BookingWizard";

export const metadata = {
    title: "Agendar Cita",
    description: "Reserva tu cita médica con la Dra. Lina María Valencia Arias en Rovira, Tolima.",
};

export default function ReservarPage() {
    return (
        <div className="pt-24 pb-16">
            <div className="max-w-2xl mx-auto px-6">
                <h1 className="text-3xl md:text-4xl font-bold text-slate-900 text-center">
                    Agendar Cita
                </h1>
                <p className="mt-3 text-slate-500 text-center text-lg">
                    Selecciona doctor, servicio y horario en minutos.
                </p>
                <div className="mt-10">
                    <BookingWizard />
                </div>
            </div>
        </div>
    );
}
