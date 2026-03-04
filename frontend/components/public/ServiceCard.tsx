import type { Service } from "@/lib/types";

export default function ServiceCard({ service }: { service: Service }) {
    return (
        <div className="bg-white rounded-2xl border border-slate-100 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center">
                <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342" />
                </svg>
            </div>
            <h3 className="mt-4 text-base font-bold text-slate-900">
                {service.name}
            </h3>
            <div className="mt-2 flex items-center gap-3 text-sm text-slate-500">
                <span>{service.duration_minutes} min</span>
                <span className="w-1 h-1 rounded-full bg-slate-300" />
                <span className="font-semibold text-indigo-600">
                    ${service.price.toLocaleString()}
                </span>
            </div>
        </div>
    );
}
