'use client';

import { useEffect, useState } from 'react';
import { RevolutionHero } from '@/components/ui/revolution-hero';
import { Testimonial } from '@/components/ui/design-testimonial';
import AnimatedCardStack from '@/components/ui/animate-card-animation';
import { Footer } from '@/components/ui/footer';
import { authClient } from '@/lib/auth-client';
import { motion } from 'framer-motion';
import { Calendar, Tag, Zap, CheckCircle } from 'lucide-react';

const features = [
  {
    icon: CheckCircle,
    title: "Task Management",
    description: "Create, organize, and track your tasks with ease"
  },
  {
    icon: Calendar,
    title: "Calendar View",
    description: "Visualize your schedule and plan ahead"
  },
  {
    icon: Tag,
    title: "Smart Tags",
    description: "Categorize and filter tasks instantly"
  },
  {
    icon: Zap,
    title: "Quick Actions",
    description: "Keyboard shortcuts for power users"
  }
];

function FeaturesSection() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 font-chelsea">
            Everything you need to stay{' '}
            <span className="bg-gradient-to-r from-aura-purple via-aura-magenta to-aura-gold bg-clip-text text-transparent">
              organized
            </span>
          </h2>
          <p className="text-white/50 max-w-2xl mx-auto">
            Powerful features designed to help you manage your tasks efficiently
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: false, amount: 0.3 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5, transition: { duration: 0.2 } }}
              className="group p-6 rounded-2xl border border-white/10 bg-black/30 backdrop-blur-xl hover:border-aura-purple/30 transition-all"
            >
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-aura-purple/20 to-aura-magenta/20 flex items-center justify-center mb-4 group-hover:from-aura-purple/30 group-hover:to-aura-magenta/30 transition-all">
                <feature.icon className="w-6 h-6 text-aura-purple" strokeWidth={1.5} />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2 font-chelsea">{feature.title}</h3>
              <p className="text-white/50 text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CardStackSection() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 font-chelsea">
            Explore our{' '}
            <span className="bg-gradient-to-r from-aura-purple via-aura-magenta to-aura-gold bg-clip-text text-transparent">
              products
            </span>
          </h2>
          <p className="text-white/50 max-w-2xl mx-auto">
            Discover what makes our todo app special
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 0.6 }}
        >
          <AnimatedCardStack />
        </motion.div>
      </div>
    </section>
  );
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const result = await authClient.getSession();
        setIsAuthenticated(!!result?.data?.user);
      } catch (error) {
        console.error('Failed to check authentication:', error);
      }
    };

    checkAuth();
  }, []);

  return (
    <main className="min-h-screen">
      <RevolutionHero isAuthenticated={isAuthenticated} />
      <Testimonial />
      <FeaturesSection />
      <CardStackSection />
      <Footer />
    </main>
  );
}
