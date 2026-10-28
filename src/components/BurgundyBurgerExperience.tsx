import React, { useState } from 'react';
import { Utensils, Flame, Sparkles, ArrowRight, Award, Clock, Star } from 'lucide-react';

export default function BurgundyBurgerExperience() {
  const [separation, setSeparation] = useState(35); // 0 to 100

  return (
    <div style={{ backgroundColor: '#FDFBF7', color: '#4A0E17', minHeight: '100vh', fontFamily: "'Plus Jakarta Sans', Inter, sans-serif", paddingBottom: '80px', borderRadius: '20px', overflow: 'hidden', border: '1px solid #EADDD5' }}>
      {/* Navbar */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '24px 40px', borderBottom: '1px solid #E5D5CC', background: '#FFFDF9' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 800, fontSize: '20px', letterSpacing: '-0.5px' }}>
          <span style={{ background: '#4A0E17', color: '#E5A93C', padding: '8px 12px', borderRadius: '12px', display: 'grid', placeItems: 'center' }}>
            <Utensils size={20} />
          </span>
          <span>ROYALE <span style={{ color: '#E5A93C' }}>&</span> BURGUNDY</span>
        </div>
        <div style={{ display: 'flex', gap: '32px', fontSize: '14px', fontWeight: 600, color: '#4A0E17' }}>
          <a href="#story" style={{ color: 'inherit', textDecoration: 'none' }}>The Philosophy</a>
          <a href="#deconstructed" style={{ color: 'inherit', textDecoration: 'none' }}>Deconstructed Burger</a>
          <a href="#features" style={{ color: 'inherit', textDecoration: 'none' }}>Mastercraft</a>
        </div>
        <button
          className="burger-cta"
          style={{
            background: '#4A0E17',
            color: '#FDFBF7',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '14px',
            fontWeight: 700,
            cursor: 'pointer',
            transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)',
            boxShadow: '0 4px 14px rgba(74, 14, 23, 0.2)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.03)';
            e.currentTarget.style.background = '#E5A93C';
            e.currentTarget.style.color = '#4A0E17';
            e.currentTarget.style.boxShadow = '0 8px 25px rgba(229, 169, 60, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.background = '#4A0E17';
            e.currentTarget.style.color = '#FDFBF7';
            e.currentTarget.style.boxShadow = '0 4px 14px rgba(74, 14, 23, 0.2)';
          }}
        >
          Reserve Table <ArrowRight size={16} style={{ display: 'inline', marginLeft: '6px', verticalAlign: 'middle' }} />
        </button>
      </nav>

      {/* Split Hero Section */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '50px', padding: '60px 40px', alignItems: 'center', position: 'relative', overflow: 'hidden' }}>
        {/* Background Liquid Silk Organic Reveal */}
        <div style={{ position: 'absolute', top: '-50px', left: '-50px', width: '500px', height: '500px', background: 'radial-gradient(circle, rgba(74,14,23,0.12) 0%, rgba(107,29,47,0.05) 70%, transparent 100%)', borderRadius: '50%', filter: 'blur(60px)', zIndex: 0, animation: 'floatBlob 10s ease-in-out infinite alternate' }} />

        {/* Left: Staggered Text Fades */}
        <div style={{ position: 'relative', zIndex: 1, animation: 'fadeInUp 0.8s cubic-bezier(0.25, 1, 0.5, 1) both' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#F4E5E1', color: '#4A0E17', padding: '6px 14px', borderRadius: '20px', fontSize: '12px', fontWeight: 700, marginBottom: '20px', letterSpacing: '1px', textTransform: 'uppercase' }}>
            <Sparkles size={14} /> Haute Cuisine Meets Smash Burgers
          </div>
          <h1 style={{ fontSize: 'clamp(40px, 4vw, 56px)', lineHeight: 1.1, fontWeight: 900, color: '#4A0E17', marginBottom: '20px', letterSpacing: '-1.5px' }}>
            The Art of <span style={{ color: '#E5A93C', fontStyle: 'italic', fontFamily: 'serif' }}>Burgery</span> & <span style={{ color: '#4A0E17', borderBottom: '3px solid #E5A93C' }}>Burgundy</span>.
          </h1>
          <p style={{ fontSize: '16px', color: '#796B70', lineHeight: 1.6, marginBottom: '32px', maxWidth: '480px' }}>
            An uncompromising culinary exploration pairing rare vintage cellar reserves with 45-day dry-aged Wagyu patties, artisan brioche, and molten cave-aged Gruyère.
          </p>
          <div style={{ display: 'flex', gap: '16px' }}>
            <button
              style={{
                background: '#4A0E17',
                color: '#FDFBF7',
                border: 'none',
                padding: '16px 28px',
                borderRadius: '16px',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)',
                boxShadow: '0 6px 20px rgba(74, 14, 23, 0.25)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.03)';
                e.currentTarget.style.background = '#E5A93C';
                e.currentTarget.style.color = '#4A0E17';
                e.currentTarget.style.boxShadow = '0 10px 30px rgba(229, 169, 60, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.background = '#4A0E17';
                e.currentTarget.style.color = '#FDFBF7';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(74, 14, 23, 0.25)';
              }}
            >
              Explore Menu
            </button>
            <button
              style={{
                background: 'transparent',
                color: '#4A0E17',
                border: '2px solid #4A0E17',
                padding: '16px 28px',
                borderRadius: '16px',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(74, 14, 23, 0.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
              }}
            >
              Watch Film
            </button>
          </div>
        </div>

        {/* Right: Deconstructed Burger Interactive Workspace */}
        <div id="deconstructed" style={{ position: 'relative', background: '#FFFDF9', borderRadius: '24px', padding: '30px', border: '1px solid #EADDD5', boxShadow: '0 20px 50px rgba(74,14,23,0.08)', display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 1 }}>
          <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <span style={{ fontSize: '13px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '1px', color: '#4A0E17' }}>
              Interactive Deconstructed Burger
            </span>
            <span style={{ fontSize: '12px', background: '#E5A93C', color: '#4A0E17', padding: '4px 10px', borderRadius: '8px', fontWeight: 700 }}>
              Exploded View: {separation}%
            </span>
          </div>

          {/* Slider control */}
          <div style={{ width: '100%', marginBottom: '30px' }}>
            <input
              type="range"
              min="0"
              max="100"
              value={separation}
              onChange={(e) => setSeparation(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#4A0E17', cursor: 'pointer' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#796B70', marginTop: '4px', fontWeight: 600 }}>
              <span>Assembled</span>
              <span>Fully Exploded</span>
            </div>
          </div>

          {/* Burger Layers Stack */}
          <div style={{ width: '100%', height: '340px', position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            {/* Top Bun */}
            <div
              style={{
                position: 'absolute',
                transform: `translateY(${-separation * 1.8}px)`,
                transition: 'transform 0.1s ease-out',
                width: '220px',
                height: '65px',
                background: 'linear-gradient(135deg, #C68B59, #9A5310)',
                borderRadius: '110px 110px 20px 20px',
                boxShadow: '0 8px 20px rgba(0,0,0,0.15)',
                display: 'grid',
                placeItems: 'center',
                color: '#FFF',
                fontWeight: 800,
                fontSize: '12px',
                letterSpacing: '.5px',
                borderBottom: '4px solid #E5A93C'
              }}
            >
              BRIOCHE CROWN
              {separation > 20 && (
                <div style={{ position: 'absolute', right: '-180px', background: '#4A0E17', color: '#FFF', padding: '6px 12px', borderRadius: '8px', fontSize: '11px', whiteSpace: 'nowrap', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
                  ✨ Artisan French Brioche with Sesame
                </div>
              )}
            </div>

            {/* Melted Cheese */}
            <div
              style={{
                position: 'absolute',
                transform: `translateY(${-separation * 0.9}px)`,
                transition: 'transform 0.1s ease-out',
                width: '200px',
                height: '35px',
                background: '#E5A93C',
                borderRadius: '16px',
                boxShadow: '0 6px 15px rgba(229,169,60,0.3)',
                display: 'grid',
                placeItems: 'center',
                color: '#4A0E17',
                fontWeight: 800,
                fontSize: '11px'
              }}
            >
              CAVE-AGED GRUYÈRE
              {separation > 30 && (
                <div style={{ position: 'absolute', left: '-180px', background: '#4A0E17', color: '#FFF', padding: '6px 12px', borderRadius: '8px', fontSize: '11px', whiteSpace: 'nowrap', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
                  🧀 18-Month Aged Swiss Gruyère
                </div>
              )}
            </div>

            {/* Thick Patty */}
            <div
              style={{
                position: 'absolute',
                transform: `translateY(0px)`,
                transition: 'transform 0.1s ease-out',
                width: '230px',
                height: '55px',
                background: '#4A0E17',
                borderRadius: '28px',
                boxShadow: '0 10px 25px rgba(74,14,23,0.3)',
                display: 'grid',
                placeItems: 'center',
                color: '#E5A93C',
                fontWeight: 900,
                fontSize: '13px',
                border: '2px solid #E5A93C'
              }}
            >
              45-DAY DRY-AGED WAGYU
              {separation > 40 && (
                <div style={{ position: 'absolute', right: '-180px', background: '#4A0E17', color: '#FFF', padding: '6px 12px', borderRadius: '8px', fontSize: '11px', whiteSpace: 'nowrap', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
                  🥩 Prime A5 Wagyu & Chuck Blend
                </div>
              )}
            </div>

            {/* Lettuce & Tomato */}
            <div
              style={{
                position: 'absolute',
                transform: `translateY(${separation * 0.9}px)`,
                transition: 'transform 0.1s ease-out',
                width: '210px',
                height: '30px',
                background: '#24785B',
                borderRadius: '14px',
                boxShadow: '0 6px 15px rgba(36,120,91,0.2)',
                display: 'grid',
                placeItems: 'center',
                color: '#FFF',
                fontWeight: 800,
                fontSize: '11px'
              }}
            >
              HEIRLOOM TOMATO & BIBB
              {separation > 50 && (
                <div style={{ position: 'absolute', left: '-180px', background: '#4A0E17', color: '#FFF', padding: '6px 12px', borderRadius: '8px', fontSize: '11px', whiteSpace: 'nowrap', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
                  🍅 Vine-Ripened Organic Produce
                </div>
              )}
            </div>

            {/* Bottom Bun */}
            <div
              style={{
                position: 'absolute',
                transform: `translateY(${separation * 1.8}px)`,
                transition: 'transform 0.1s ease-out',
                width: '220px',
                height: '50px',
                background: 'linear-gradient(135deg, #C68B59, #9A5310)',
                borderRadius: '20px 20px 100px 100px',
                boxShadow: '0 8px 20px rgba(0,0,0,0.15)',
                display: 'grid',
                placeItems: 'center',
                color: '#FFF',
                fontWeight: 800,
                fontSize: '12px'
              }}
            >
              TOASTED HEEL
              {separation > 60 && (
                <div style={{ position: 'absolute', right: '-180px', background: '#4A0E17', color: '#FFF', padding: '6px 12px', borderRadius: '8px', fontSize: '11px', whiteSpace: 'nowrap', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
                  🧈 Cultured French Butter Toast
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* 3 Product Feature Cards Grid */}
      <section id="features" style={{ padding: '40px 40px 20px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '32px', fontWeight: 900, color: '#4A0E17', marginBottom: '10px' }}>The Mastercraft Pillars</h2>
          <p style={{ color: '#796B70', fontSize: '15px' }}>Where gourmet burger craft meets the sophistication of grand cru Burgundy.</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '30px' }}>
          {/* Card 1 */}
          <div
            className="feature-card"
            style={{
              background: '#4A0E17',
              color: '#FFFDF9',
              borderRadius: '24px',
              padding: '36px',
              transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)',
              boxShadow: '0 12px 30px rgba(74, 14, 23, 0.15)',
              position: 'relative',
              overflow: 'hidden',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-10px)';
              e.currentTarget.style.boxShadow = '0 20px 45px rgba(74, 14, 23, 0.3)';
              const p = e.currentTarget.querySelector('.card-desc') as HTMLElement;
              if (p) {
                p.style.opacity = '1';
                p.style.transform = 'translateY(0)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 12px 30px rgba(74, 14, 23, 0.15)';
              const p = e.currentTarget.querySelector('.card-desc') as HTMLElement;
              if (p) {
                p.style.opacity = '0.6';
                p.style.transform = 'translateY(8px)';
              }
            }}
          >
            <div style={{ background: '#E5A93C', color: '#4A0E17', width: '48px', height: '48px', borderRadius: '14px', display: 'grid', placeItems: 'center', marginBottom: '24px', fontWeight: 800 }}>
              <Award size={24} />
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '12px', color: '#FFFDF9' }}>45-Day Dry-Aged Wagyu</h3>
            <p className="card-desc" style={{ color: '#EADDD5', fontSize: '14px', lineHeight: 1.6, opacity: 0.6, transform: 'translateY(8px)', transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)' }}>
              Hand-selected prime cuts dry-aged in Himalayan salt chambers for deep, buttery umami notes that melt instantly upon contact.
            </p>
          </div>

          {/* Card 2 */}
          <div
            className="feature-card"
            style={{
              background: '#4A0E17',
              color: '#FFFDF9',
              borderRadius: '24px',
              padding: '36px',
              transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)',
              boxShadow: '0 12px 30px rgba(74, 14, 23, 0.15)',
              position: 'relative',
              overflow: 'hidden',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-10px)';
              e.currentTarget.style.boxShadow = '0 20px 45px rgba(74, 14, 23, 0.3)';
              const p = e.currentTarget.querySelector('.card-desc') as HTMLElement;
              if (p) {
                p.style.opacity = '1';
                p.style.transform = 'translateY(0)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 12px 30px rgba(74, 14, 23, 0.15)';
              const p = e.currentTarget.querySelector('.card-desc') as HTMLElement;
              if (p) {
                p.style.opacity = '0.6';
                p.style.transform = 'translateY(8px)';
              }
            }}
          >
            <div style={{ background: '#E5A93C', color: '#4A0E17', width: '48px', height: '48px', borderRadius: '14px', display: 'grid', placeItems: 'center', marginBottom: '24px', fontWeight: 800 }}>
              <Clock size={24} />
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '12px', color: '#FFFDF9' }}>Grand Cru Pairings</h3>
            <p className="card-desc" style={{ color: '#EADDD5', fontSize: '14px', lineHeight: 1.6, opacity: 0.6, transform: 'translateY(8px)', transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)' }}>
              Curated sommelier selections featuring exquisite Côte de Nuits and Côte de Beaune Pinot Noir reserves to elevate every bite.
            </p>
          </div>

          {/* Card 3 */}
          <div
            className="feature-card"
            style={{
              background: '#4A0E17',
              color: '#FFFDF9',
              borderRadius: '24px',
              padding: '36px',
              transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)',
              boxShadow: '0 12px 30px rgba(74, 14, 23, 0.15)',
              position: 'relative',
              overflow: 'hidden',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-10px)';
              e.currentTarget.style.boxShadow = '0 20px 45px rgba(74, 14, 23, 0.3)';
              const p = e.currentTarget.querySelector('.card-desc') as HTMLElement;
              if (p) {
                p.style.opacity = '1';
                p.style.transform = 'translateY(0)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 12px 30px rgba(74, 14, 23, 0.15)';
              const p = e.currentTarget.querySelector('.card-desc') as HTMLElement;
              if (p) {
                p.style.opacity = '0.6';
                p.style.transform = 'translateY(8px)';
              }
            }}
          >
            <div style={{ background: '#E5A93C', color: '#4A0E17', width: '48px', height: '48px', borderRadius: '14px', display: 'grid', placeItems: 'center', marginBottom: '24px', fontWeight: 800 }}>
              <Star size={24} />
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '12px', color: '#FFFDF9' }}>Molten Cave Gruyère</h3>
            <p className="card-desc" style={{ color: '#EADDD5', fontSize: '14px', lineHeight: 1.6, opacity: 0.6, transform: 'translateY(8px)', transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)' }}>
              Authentic Swiss Gruyère aged 18 months in medieval limestone cellars, creating an exceptionally rich, nutty velvet melt.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
