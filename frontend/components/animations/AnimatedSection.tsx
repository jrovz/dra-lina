"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface AnimatedSectionProps {
    children: ReactNode;
    className?: string;
    delay?: number;
    direction?: "up" | "down" | "left" | "right" | "none";
}

export function AnimatedSection({
    children,
    className = "",
    delay = 0,
    direction = "up"
}: AnimatedSectionProps) {

    const getInitialY = () => direction === "up" ? 50 : direction === "down" ? -50 : 0;
    const getInitialX = () => direction === "left" ? 50 : direction === "right" ? -50 : 0;

    return (
        <motion.div
            initial={{
                opacity: 0,
                y: getInitialY(),
                x: getInitialX()
            }}
            whileInView={{
                opacity: 1,
                y: 0,
                x: 0
            }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{
                duration: 0.8,
                delay: delay,
                ease: [0.21, 0.47, 0.32, 0.98] // custom smooth ease-out
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

export function StaggerContainer({ children, className = "" }: { children: ReactNode, className?: string }) {
    return (
        <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={{
                hidden: {},
                visible: {
                    transition: {
                        staggerChildren: 0.15
                    }
                }
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

export function StaggerItem({ children, className = "" }: { children: ReactNode, className?: string }) {
    return (
        <motion.div
            variants={{
                hidden: { opacity: 0, y: 30 },
                visible: {
                    opacity: 1,
                    y: 0,
                    transition: {
                        duration: 0.6,
                        ease: "easeOut"
                    }
                }
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}
