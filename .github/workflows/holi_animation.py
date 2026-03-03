from manim import *
import numpy as np
import random

class HoliManifold(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.camera.set_focal_distance(20)

        # ── Part 1: Holi chaos – colorful particle cloud ────────────────────────
        NUM_PARTICLES = 2200
        particles = VGroup()
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, TEAL]

        for _ in range(NUM_PARTICLES):
            theta = random.uniform(0, TAU)
            phi = random.uniform(0, PI)
            r = random.uniform(0.05, 3.8)   # spread radius

            pos = np.array([
                r * np.sin(phi) * np.cos(theta),
                r * np.sin(phi) * np.sin(theta),
                r * np.cos(phi) * 0.7   # slightly flattened
            ])

            dot = Dot3D(
                point=pos,
                radius=0.035 + random.uniform(-0.012, 0.018),
                color=random.choice(colors),
                glow_factor=1.2
            )
            particles.add(dot)

        # Add some initial random motion to particles
        def particle_updater(mob, dt):
            for dot in mob:
                # small brownian-like jiggle + slow outward drift
                drift = np.array([
                    random.gauss(0, 0.014),
                    random.gauss(0, 0.014),
                    random.gauss(0, 0.008)
                ])
                dot.shift(drift * 1.5)
                # fade older particles slightly (optional artistic touch)
                if np.linalg.norm(dot.get_center()) > 6:
                    dot.set_opacity(dot.get_opacity() * 0.97)

        particles.add_updater(particle_updater)

        self.play(Create(particles, lag_ratio=0.004, run_time=5), run_time=6)
        self.wait(1.5)

        title = Text("Holi on Manifolds", font_size=48).to_edge(UP, buff=0.4)
        self.play(Write(title))

        self.wait(1)

        # ── Part 2: Coalesce particles → torus manifold ─────────────────────────
        torus = Torus(
            major_radius=2.8,
            minor_radius=0.9,
            resolution=(48, 32),
            color=TEAL,
            opacity=0.35,
            checkerboard_colors=False
        )

        # colorful parametric surface version
        def colorful_torus(u, v):
            R, r = 2.8, 0.9
            x = (R + r * np.cos(v)) * np.cos(u)
            y = (R + r * np.cos(v)) * np.sin(u)
            z = r * np.sin(v)
            return np.array([x, y, z])

        color_torus = Surface(
            colorful_torus,
            u_range=[0, TAU],
            v_range=[0, TAU],
            resolution=(36, 24),
            checkerboard_colors=[PINK, YELLOW, TEAL, PURPLE],
            fill_opacity=0.7,
            stroke_width=0.4,
            stroke_color=WHITE
        )

        self.play(
            particles.animate.set_opacity(0.15).scale(0.6),
            FadeIn(torus),
            run_time=3
        )
        self.play(Transform(torus, color_torus), run_time=3.5)
        self.wait(1.5)

        # Highlight a non-contractible loop (pink)
        loop = ParametricFunction(
            lambda t: np.array([
                (2.8 + 0.9 * np.cos(0)) * np.cos(t),
                (2.8 + 0.9 * np.cos(0)) * np.sin(t),
                0.9 * np.sin(0)
            ]),
            t_range=[0, TAU],
            color=PINK,
            stroke_width=8
        )

        loop_text = Tex(r"$\pi_1 \neq 0$", color=PINK, font_size=60).next_to(loop, OUT + RIGHT, buff=0.8)

        self.play(Create(loop), Write(loop_text), run_time=2.5)
        self.wait(2)

        # ── Part 3: Functor-like color transfer (simple sphere → torus map) ─────
        sphere = Sphere(
            radius=1.4,
            resolution=(24, 18),
            color=BLUE_E,
            opacity=0.5
        ).shift(LEFT * 5 + DOWN * 0.5)

        self.play(
            torus.animate.shift(RIGHT * 4.5),
            FadeIn(sphere),
            title.animate.shift(UP * 0.4).scale(0.8),
            run_time=2.5
        )

        # "Functor" as colored particles flowing from sphere to torus
        flow_arrows = VGroup()
        for _ in range(80):
            start = sphere.sample_point_inside() + RIGHT * random.uniform(-0.1, 0.1)
            end = color_torus.sample_point_inside() + LEFT * random.uniform(-0.1, 0.1)
            arrow = Arrow3D(start, end, color=random.choice([YELLOW, PINK, TEAL]), stroke_width=3)
            flow_arrows.add(arrow)

        self.play(
            LaggedStartMap(Create, flow_arrows, lag_ratio=0.04),
            run_time=4
        )

        nat_trans_text = Tex(r"functor $\mathbf{F}$", font_size=54, color=YELLOW).next_to(flow_arrows, UP, buff=1.2)
        self.play(Write(nat_trans_text))

        self.wait(2.5)

        # ── Ending ───────────────────────────────────────────────────────────────
        self.play(
            *[FadeOut(mob) for mob in self.mobjects if mob is not title],
            title.animate.center().scale(1.4),
            run_time=3
        )

        final_text = Text("Happy Holi!\nfrom topology & categories", font_size=48).next_to(title, DOWN, buff=0.8)
        self.play(Write(final_text))
        self.wait(4)

        self.play(FadeOut(VGroup(title, final_text)))
