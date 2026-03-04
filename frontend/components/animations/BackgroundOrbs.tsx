"use client";

import { motion } from "framer-motion";

export function BackgroundOrbs() {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
            {/* Orb 1: Top Right (Indigo) */}
            <motion.div
                animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.3, 0.5, 0.3],
                    x: [0, -30, 0],
                    y: [0, 40, 0],
                }}
                transition={{
                    duration: 15,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
                className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-indigo-300 rounded-full blur-[100px] opacity-30 mix-blend-multiply"
            />

            {/* Orb 2: Bottom Left (Violet) */}
            <motion.div
                animate={{
                    scale: [1, 1.3, 1],
                    opacity: [0.2, 0.4, 0.2],
                    x: [0, 50, 0],
                    y: [0, -30, 0],
                }}
                transition={{
                    duration: 18,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 2,
                }}
                className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-violet-300 rounded-full blur-[120px] opacity-20 mix-blend-multiply"
            />

            {/* Orb 3: Center (Fuchsia/Pink abstract touch) */}
            <motion.div
                animate={{
                    scale: [1, 1.4, 1],
                    opacity: [0.1, 0.25, 0.1],
                }}
                transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 5,
                }}
                className="absolute top-[30%] left-[40%] w-[400px] h-[400px] bg-fuchsia-200 rounded-full blur-[100px] opacity-10 mix-blend-multiply"
            />
        </div>
    );
}
