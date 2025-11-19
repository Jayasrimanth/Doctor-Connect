import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Calendar, MessageSquare, Stethoscope, ArrowRight } from "lucide-react";
import { useState, useEffect } from "react";
import dashboardHero from "@/assets/dashboard-hero.jpg";

const Dashboard = () => {
  const navigate = useNavigate();
  const [messageIndex, setMessageIndex] = useState(0);

  const sampleMessages = [
    { role: "user", text: "Hi, I need to book an appointment" },
    { role: "bot", text: "Hello! I'd be happy to help you book an appointment. May I have your full name please?" },
    { role: "user", text: "My name is Sarah Johnson" },
    { role: "bot", text: "Nice to meet you, Sarah! Could you please provide your email address?" },
    { role: "user", text: "It's sarah.johnson@email.com" },
    { role: "bot", text: "Thank you! What brings you in today? Please describe your symptoms or reason for the visit." },
  ];

  useEffect(() => {
    if (messageIndex < sampleMessages.length) {
      const timer = setTimeout(() => {
        setMessageIndex(prev => prev + 1);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [messageIndex]);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${dashboardHero})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary/90 via-primary/70 to-accent/80 backdrop-blur-[2px]"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <div className="flex justify-center mb-6">
              <div className="bg-white/20 backdrop-blur-sm p-4 rounded-full border border-white/30">
                <Stethoscope className="h-12 w-12 text-white" />
              </div>
            </div>
            <h1 className="text-5xl font-bold mb-4 text-white drop-shadow-lg">
              Welcome to HealthConnect
            </h1>
            <p className="text-xl text-white/90 max-w-2xl mx-auto drop-shadow">
              Book your doctor appointment in minutes with our AI-powered assistant
            </p>
          </div>

          {/* How It Works Section */}
          <div className="mb-12 animate-slide-up">
            <h2 className="text-3xl font-semibold text-center mb-8 text-white drop-shadow-lg">
              How It Works
            </h2>
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="p-6 text-center hover:shadow-xl transition-all bg-white/95 backdrop-blur-sm border-white/20 hover:scale-105">
                <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MessageSquare className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">1. Chat with AI</h3>
                <p className="text-muted-foreground">
                  Share your symptoms and preferences with our intelligent assistant
                </p>
              </Card>

              <Card className="p-6 text-center hover:shadow-xl transition-all bg-white/95 backdrop-blur-sm border-white/20 hover:scale-105">
                <div className="bg-secondary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Stethoscope className="h-8 w-8 text-secondary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">2. Get Recommendations</h3>
                <p className="text-muted-foreground">
                  Receive personalized doctor recommendations based on your needs
                </p>
              </Card>

              <Card className="p-6 text-center hover:shadow-xl transition-all bg-white/95 backdrop-blur-sm border-white/20 hover:scale-105">
                <div className="bg-accent/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Calendar className="h-8 w-8 text-accent" />
                </div>
                <h3 className="text-xl font-semibold mb-2">3. Confirm Booking</h3>
                <p className="text-muted-foreground">
                  Choose your preferred time and confirm your appointment instantly
                </p>
              </Card>
            </div>
          </div>

          {/* Live Chat Preview */}
          <Card className="p-6 mb-8 animate-slide-up bg-white/95 backdrop-blur-sm border-white/20 shadow-2xl">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              Live Chat Preview
            </h3>
            <div className="bg-muted/50 rounded-lg p-4 h-64 overflow-y-auto space-y-3">
              {sampleMessages.slice(0, messageIndex).map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
                >
                  <div
                    className={`max-w-[80%] px-4 py-2 rounded-lg ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-card text-card-foreground border border-border"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              {messageIndex < sampleMessages.length && (
                <div className="flex justify-start animate-fade-in">
                  <div className="bg-card text-card-foreground border border-border px-4 py-2 rounded-lg">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* CTA Button */}
          <div className="text-center animate-slide-up">
            <Button
              size="lg"
              onClick={() => navigate("/chat")}
              className="text-lg px-8 py-6 shadow-lg hover:shadow-xl transition-all"
            >
              Book Appointment Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
