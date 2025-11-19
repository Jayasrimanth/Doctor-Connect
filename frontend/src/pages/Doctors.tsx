import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Star, Calendar, Award, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import doctorsBackground from "@/assets/doctors-background.jpg";

interface Doctor {
  id: string;
  name: string;
  specialization: string;
  experience: number;
  image_url: string;
  rating?: number;
  isRecommended?: boolean;
}

const Doctors = () => {
  const [selectedDoctor, setSelectedDoctor] = useState<string | null>(null);

  // Mock doctor data - in production, this would be fetched from /api/doctors
  const doctors: Doctor[] = [
    {
      id: "1",
      name: "Dr. Pavan Kumar",
      specialization: "General Practitioner",
      experience: 12,
      image_url: "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop",
      rating: 4.9,
      isRecommended: true,
    },
  ];

  const recommendedDoctor = doctors.find(d => d.isRecommended);

  const handleConfirmBooking = async (doctorId: string, doctorName: string) => {
    setSelectedDoctor(doctorId);
    
    try {
      // Mock API call - in production, this would call /api/book
      // const response = await fetch('/api/book', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ doctorId, datetime: selectedDateTime })
      // });

      setTimeout(() => {
        toast.success(`Appointment confirmed with ${doctorName}!`, {
          description: "You'll receive a confirmation email shortly.",
        });
        setSelectedDoctor(null);
      }, 1500);
    } catch (error) {
      toast.error("Failed to confirm booking. Please try again.");
      setSelectedDoctor(null);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${doctorsBackground})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary/88 via-primary/78 to-secondary/75 backdrop-blur-[4px]"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8 animate-fade-in">
            <h1 className="text-4xl font-bold mb-2 text-white drop-shadow-lg">Select Your Doctor</h1>
            <p className="text-white/90 drop-shadow">Choose from our experienced medical professionals</p>
          </div>

          {/* Recommended Doctor Section */}
          {recommendedDoctor && (
            <Card className="mb-8 p-6 border-2 border-white/30 shadow-2xl animate-slide-up bg-white/95 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-4">
                <Star className="h-6 w-6 text-primary fill-primary" />
                <h2 className="text-2xl font-semibold text-foreground">Recommended for You</h2>
              </div>
              <div className="flex flex-col md:flex-row gap-6 items-center">
                <img
                  src={recommendedDoctor.image_url}
                  alt={recommendedDoctor.name}
                  className="w-32 h-32 rounded-full object-cover border-4 border-primary"
                />
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-2xl font-bold mb-2">{recommendedDoctor.name}</h3>
                  <div className="flex flex-wrap gap-2 justify-center md:justify-start mb-3">
                    <Badge variant="secondary" className="text-sm">
                      {recommendedDoctor.specialization}
                    </Badge>
                    <Badge variant="outline" className="text-sm">
                      <Award className="h-3 w-3 mr-1" />
                      {recommendedDoctor.experience} years
                    </Badge>
                    <Badge variant="outline" className="text-sm">
                      <Star className="h-3 w-3 mr-1 fill-current" />
                      {recommendedDoctor.rating}
                    </Badge>
                  </div>
                  <p className="text-muted-foreground mb-4">
                    Based on your symptoms, Dr. {recommendedDoctor.name.split(" ")[1]} is the best match for your needs.
                  </p>
                  <Button
                    size="lg"
                    onClick={() => handleConfirmBooking(recommendedDoctor.id, recommendedDoctor.name)}
                    disabled={selectedDoctor === recommendedDoctor.id}
                    className="shadow-lg"
                  >
                    {selectedDoctor === recommendedDoctor.id ? (
                      <>Processing...</>
                    ) : (
                      <>
                        <CheckCircle2 className="mr-2 h-5 w-5" />
                        Confirm Booking
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* All Doctors Grid */}
          <div>
            <h2 className="text-2xl font-semibold mb-6 text-white drop-shadow-lg">All Available Doctors</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {doctors.map((doctor, index) => (
                <Card
                  key={doctor.id}
                  className={`p-6 hover:shadow-2xl transition-all animate-slide-up bg-white/95 backdrop-blur-sm border-white/20 hover:scale-105 ${
                    doctor.isRecommended ? "border-2 border-white/40 ring-2 ring-white/20" : ""
                  }`}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex flex-col items-center text-center">
                    <div className="relative mb-4">
                      <img
                        src={doctor.image_url}
                        alt={doctor.name}
                        className="w-24 h-24 rounded-full object-cover border-2 border-border"
                      />
                      {doctor.isRecommended && (
                        <div className="absolute -top-2 -right-2 bg-primary rounded-full p-1">
                          <Star className="h-4 w-4 text-primary-foreground fill-current" />
                        </div>
                      )}
                    </div>
                    
                    <h3 className="text-xl font-bold mb-2">{doctor.name}</h3>
                    
                    <div className="flex flex-col gap-2 mb-4 w-full">
                      <Badge variant="secondary" className="justify-center">
                        {doctor.specialization}
                      </Badge>
                      <div className="flex gap-2 justify-center">
                        <Badge variant="outline" className="text-xs">
                          <Award className="h-3 w-3 mr-1" />
                          {doctor.experience}y
                        </Badge>
                        {doctor.rating && (
                          <Badge variant="outline" className="text-xs">
                            <Star className="h-3 w-3 mr-1 fill-current" />
                            {doctor.rating}
                          </Badge>
                        )}
                      </div>
                    </div>

                    <Button
                      variant={doctor.isRecommended ? "default" : "outline"}
                      className="w-full"
                      onClick={() => handleConfirmBooking(doctor.id, doctor.name)}
                      disabled={selectedDoctor === doctor.id}
                    >
                      {selectedDoctor === doctor.id ? (
                        "Processing..."
                      ) : (
                        <>
                          <Calendar className="mr-2 h-4 w-4" />
                          Book Appointment
                        </>
                      )}
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Doctors;
