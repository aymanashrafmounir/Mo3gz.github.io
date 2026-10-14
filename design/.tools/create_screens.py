"""Author editable portfolio screens through the real Figcraft MCP engine.

Design automation only. No portfolio application code is generated here.
"""
import json
import pathlib
import sys
from figcraft_mcp import Figcraft

ROOT = pathlib.Path(__file__).resolve().parents[2]
DESIGN = ROOT / "design"
DATA = json.loads((DESIGN / "screen-content.json").read_text(encoding="utf-8-sig"))
PROJECTS = DATA["projects"]
PAPER, SURFACE, TEXT, MUTED, RUST, FOCUS = "#F5F2EC", "#EEE7DE", "#26251F", "#645D53", "#AE3A24", "#8B2F20"
LINE, QUIET = "#D4C9BC", "#70675D"
CV_URL = "file:///D:/aymanashraf.me/Ayman%20Kamel%20-%20CV.pdf"
CAREER = [
    ("Software Engineer, Backend Focus", "Freelance", "Jul 2025 to Present", "Backend systems, REST APIs and full product delivery, from requirements through production support."),
    ("AI Evaluation & Benchmarking Contributor", "Freelance / Contract", "May 2025 to Present", "Technical task specifications, verification criteria and edge cases for agentic and coding benchmarks."),
    ("Junior Software Engineer", "Blitz Armada", "Oct 2025 to Mar 2026", "Backend features, system architecture contributions and collaborative enterprise application delivery."),
    ("Software Engineer Intern", "AZM Squad", "Jul 2025 to Oct 2025", "Java Spring Boot microservices and frontend integration within Agile/SCRUM teams."),
    ("Software Engineer Intern", "Siemens Digital Industries Software", "Oct 2023 to Feb 2024", "C++ and Qt desktop engineering, profiling, memory optimization and refactoring."),
]
SKILLS = [
    ("Backend engineering", "Java, Spring Boot, JPA, Hono, REST APIs, Spring Security"),
    ("Frontend engineering", "React, Next.js, TypeScript, JavaScript, HTML and CSS"),
    ("Data and persistence", "PostgreSQL, MySQL, SQL Server, SQLite"),
    ("Cloud and infrastructure", "Cloudflare Workers, D1, R2, AWS, Docker, Nginx, Firebase"),
    ("Testing and quality", "Mockito, Vitest, Playwright, Miniflare, profiling"),
    ("Architecture and collaboration", "Multi-tenancy, RBAC, microservices, CI/CD, Agile, Git"),
]
CERTS = [
    ("Full Stack Web Development Mentorship", "Deloitte", "September 2024"),
    ("Linux Fundamentals Trainee", "Orange Digital Center Egypt", "September 2024"),
    ("Artificial Intelligence Training", "Huawei ICT Academy, Cairo University", "September 2023"),
    ("ICPC ECPC Qualifications", "Participant", "2023"),
]


class Screens:
    def __init__(self):
        self.mcp = Figcraft()
        self.frames = []
        self.links = []
        self.pages = {}
        self.components = {}
        self.exports = []
        self.x_positions = {}
        self.text_nodes = []
        self.current_width = None
        self.mcp.command("file.new", {"name": "Ayman Portfolio V2"})

    def node(self, kind, name, x, y, width, height=None, parent=None, props=None, text=None):
        args = dict(type=kind, name=name, x=x, y=y, width=width, props=props or {})
        if parent is not None:
            args["parent"] = parent
        if height is not None:
            args["height"] = height
        if text is not None:
            args["text"] = text
        result = self.mcp.tool("create_node", args)
        return result["id"], result["node"]

    def text(self, parent, text, x, y, width, size=18, color=TEXT, weight="Regular", name=None):
        result = self.node("text", name or text[:70], x, y, width, parent=parent, text=text,
                           props={"fontFamily": "Mona Sans", "fontStyle": weight, "fontSize": size,
                                  "lineHeight": round(size * (1.25 if size >= 64 else 1.42)), "fill": color,
                                  "textAutoResize": "height", "letterSpacing": -0.4 if size >= 36 else 0})
        self.text_nodes.append(result[0])
        return result

    def rect(self, parent, name, x, y, width, height, color=SURFACE, radius=0, stroke=None):
        props = {"fill": color, "cornerRadius": radius}
        if stroke:
            props.update(stroke=stroke, strokeWeight=1)
        return self.node("rectangle", name, x, y, width, height, parent=parent, props=props)[0]

    def divider(self, parent, x, y, width):
        self.rect(parent, "Section divider", x, y, width, 1, LINE)

    def image(self, parent, slug, x, y, width, height, caption=False):
        source = self.image_source(slug)
        if source is None:
            return None
        wrapper, _ = self.node("frame", "Original portrait" if slug == "portfolio-hero" else "Genuine public capture / " + slug, x, y, width, height, parent=parent,
                               props={"fill": SURFACE, "cornerRadius": 6, "clip": True})
        self.mcp.command("image.place", {"path": str(source),
                                         "parent": wrapper, "x": 0, "y": 0, "width": width, "height": height, "mode": "fill"})
        if caption:
            self.text(parent, "Original personal photograph" if slug == "portfolio-hero" else "Public website capture", x, y + height + 12, width, 12, QUIET)
        return wrapper

    @staticmethod
    def image_source(slug):
        if slug == "portfolio-hero":
            return DESIGN / "assets" / "personal" / "ayman-original.jpg"
        project = next(p for p in PROJECTS if p["slug"] == slug)
        capture = project.get("capture")
        path = DESIGN / "assets" / "captures" / (str(capture) + ".png")
        return path if capture and path.exists() else None

    def button(self, parent, label, x, y, width=170, primary=True, target=None, url=None):
        style = "primary" if primary else "secondary"
        instance = self.mcp.command("instance.create", {"component": self.components[style], "parent": parent, "x": x, "y": y})
        ident = instance["id"]
        self.mcp.command("node.set", {"ids": [ident], "width": width})
        self.mcp.command("instance.setProperties", {"ids": [ident], "properties": {"Label": label}})
        if target:
            self.links.append((ident, target, self.current_width))
        if url:
            self.mcp.command("proto.interaction.add", {"id": ident, "trigger": {"type": "onClick"},
                                                       "action": {"type": "openUrl", "url": url}})
        return ident

    def nav_link(self, parent, label, x, y, width, target, active=False):
        click, _ = self.node("frame", "Navigate to " + label, x, y, width, 44, parent=parent,
                              props={"fill": PAPER})
        self.text(click, label, 0, 10, width, 15, RUST if active else MUTED, "Medium")
        self.links.append((click, target, self.current_width))
        return click

    def new_frame(self, slug, width, kind="route"):
        self.current_width = width
        x = self.x_positions.get(width, 0)
        self.x_positions[width] = x + width + 220
        ident, _ = self.node("frame", slug + " / " + str(width), x, 0, width, 14000,
                              props={"fill": PAPER, "clip": True, "overflow": "vertical"})
        record = {"slug": slug, "width": width, "id": ident, "kind": kind, "page": self.pages[width]}
        self.frames.append(record)
        return ident

    def header(self, parent, width, active=None):
        margin = 80 if width >= 1200 else 40 if width >= 700 else 24
        brand_width = 310 if width >= 1200 else 250 if width >= 700 else 225
        self.nav_link(parent, "Ayman Ashraf Mounir" if width >= 700 else "Ayman Ashraf", margin, 22, brand_width, "home")
        if width >= 1200:
            for label, route, x, span in [("Projects", "projects", 825, 100), ("About", "about", 950, 70),
                                           ("Experience", "experience", 1045, 110), ("Resume", "resume", 1180, 85)]:
                self.nav_link(parent, label, x, 22, span, route, active == route)
            self.nav_link(parent, "Contact", width - margin - 70, 22, 70, "contact", active == "contact")
        else:
            self.nav_link(parent, "Menu", width - margin - 55, 22, 55, "menu-open", False)
        self.divider(parent, margin, 86, width - margin * 2)
        return margin

    def footer(self, parent, width, y):
        margin = 80 if width >= 1200 else 40 if width >= 700 else 24
        self.divider(parent, margin, y, width - margin * 2)
        self.text(parent, "Ayman Ashraf Mounir", margin, y + 28, width - margin * 2, 16, TEXT, "Medium")
        if width >= 700:
            self.text(parent, "Software Engineer, Backend Focused", margin, y + 60, 430, 14, MUTED)
            self.nav_link(parent, "GitHub", width - margin - 310, y + 23, 70, "external:github")
            self.nav_link(parent, "LinkedIn", width - margin - 210, y + 23, 80, "external:linkedin")
            self.nav_link(parent, "Contact", width - margin - 100, y + 23, 100, "contact")
        else:
            self.text(parent, "Cairo, Egypt", margin, y + 62, width - margin * 2, 14, MUTED)
            self.nav_link(parent, "GitHub", margin, y + 88, 75, "external:github")
            self.nav_link(parent, "LinkedIn", margin + 100, y + 88, 90, "external:linkedin")
            self.nav_link(parent, "Contact", margin + 215, y + 88, 90, "contact")
        bottom = y + (122 if width >= 700 else 174)
        self.mcp.command("node.set", {"ids": [parent], "height": bottom})
        return bottom

    def foundation(self):
        page = self.mcp.command("page.list")[0]["id"]
        self.mcp.command("page.rename", {"id": page, "name": "Foundations and interaction states"})
        root, _ = self.node("frame", "Design system", 0, 0, 1440, 1500, props={"fill": PAPER})
        self.foundation_id = root
        self.text(root, "Ayman Portfolio V2", 80, 70, 1280, 52, TEXT, "Bold")
        self.text(root, "Engineering shown through the work. Native design foundations.", 80, 160, 1280, 22, MUTED)
        for i, (name, color) in enumerate([("Paper", PAPER), ("Surface", SURFACE), ("Foreground", TEXT),
                                          ("Secondary", MUTED), ("Rust", RUST), ("Focus", FOCUS)]):
            swatch = self.rect(root, name, 80 + i * 210, 250, 182, 95, color, 12, LINE)
            self.text(root, name + "\n" + color, 80 + i * 210, 360, 190, 16, MUTED)
            self.mcp.command("style.create", {"type": "paint", "name": "Color/" + name, "from": swatch})
        self.text(root, "Mona Sans", 80, 460, 700, 60, TEXT, "Bold")
        self.text(root, "A calm reading voice. A committed display scale.", 80, 565, 1150, 24, MUTED)
        for j, (name, size, weight) in enumerate([("Display", 64, "Bold"), ("Heading", 36, "SemiBold"),
                                                ("Body", 18, "Regular"), ("Label", 14, "Medium")]):
            ident, _ = self.text(root, name + " " + str(size), 80, 660 + j * 105, 600, size, TEXT, weight)
            self.mcp.command("style.create", {"type": "text", "name": "Type/" + name, "from": ident})
        for key, fill, foreground, stroke in [("primary", RUST, PAPER, None), ("secondary", PAPER, TEXT, LINE)]:
            comp, _ = self.node("component", "Button/" + key.title(), 760, 685 if key == "primary" else 780, 174, 52,
                                  parent=root, props={"fill": fill, "cornerRadius": 6, "layout": "horizontal",
                                                      "padding": [14, 20], "mainAlign": "center", "crossAlign": "center",
                                                      **({"stroke": stroke, "strokeWeight": 1} if stroke else {})})
            label, _ = self.text(comp, "View projects", 0, 0, 135, 15, foreground, "SemiBold")
            self.mcp.command("node.set", {"ids": [label], "textAutoResize": "widthAndHeight"})
            self.mcp.command("component.addProperty", {"id": comp, "name": "Label", "type": "text", "default": "View projects", "layer": label})
            self.components[key] = comp
        focus = self.rect(root, "Focus ring", 752, 884, 190, 68, PAPER, 14, FOCUS)
        self.mcp.command("node.set", {"ids": [focus], "strokeWeight": 2})
        self.button(root, "Keyboard focus", 760, 892, 174)
        self.text(root, "Focus: 2px deep rust, 4px offset. Hover: deeper rust.\nTouch target: at least 44px. Disabled: no action.\nReduced motion: instant transitions and static artwork.", 760, 985, 520, 16, MUTED)
        for i, (label, fill, color) in enumerate([("Hover", "#922E1D", PAPER), ("Pressed", "#762517", PAPER), ("Disabled", SURFACE, QUIET)]):
            state, _ = self.node("component", "Button/" + label, 760 + i * 192, 1150, 174, 52,
                                  parent=root, props={"fill": fill, "cornerRadius": 6})
            self.text(state, label, 20, 14, 134, 15, color, "SemiBold")
        self.text(root, "Direction A, selected by Ayman. Warm paper and rust.\nUnchanged personal portrait and genuine project captures.\nNo generated illustrations are used in these screens.", 80, 1190, 1160, 20, MUTED)
        for width, name in [(1440, "Desktop / 1440"), (768, "Tablet / 768"), (390, "Mobile / 390")]:
            added = self.mcp.command("page.add", {"name": name})
            self.pages[width] = added["id"]

    def career_block(self, parent, x, y, width, compact=False):
        for title, company, dates, description in CAREER:
            ident, box = self.text(parent, title, x, y, width, 20 if compact else 23, TEXT, "SemiBold")
            y += box["height"] + 8
            _, box = self.text(parent, company + "  /  " + dates, x, y, width, 14 if compact else 16, FOCUS)
            y += box["height"] + 12
            _, box = self.text(parent, description, x, y, width, 16 if compact else 18, MUTED)
            y += box["height"] + 30
            self.divider(parent, x, y, width)
            y += 32
        return y

    def skill_block(self, parent, x, y, width, columns=2):
        start = y
        column_width = (width - 44 * (columns - 1)) / columns
        row_height = 156
        for i, (name, value) in enumerate(SKILLS):
            px, py = x + (i % columns) * (column_width + 44), start + (i // columns) * row_height
            self.text(parent, name, px, py, column_width, 21, TEXT, "SemiBold")
            self.text(parent, value, px, py + 42, column_width, 16, MUTED)
        return start + ((len(SKILLS) + columns - 1) // columns) * row_height

    def project_card(self, parent, project, x, y, width, image_height=235):
        if self.image_source(project["slug"]):
            self.image(parent, project["slug"], x, y, width, image_height)
        else:
            image_height = 0
            self.divider(parent, x, y, width)
        title, box = self.text(parent, project["title"], x, y + image_height + 22, width, 26, TEXT, "SemiBold")
        end = y + image_height + 22 + box["height"]
        self.text(parent, project["kind"], x, end + 8, width, 15, project["accent"])
        _, box = self.text(parent, project["summary"], x, end + 42, width, 16, MUTED)
        link_y = end + 42 + box["height"] + 15
        link = self.nav_link(parent, "Read case study", x, link_y, min(width, 170), "project:" + project["slug"])
        return link_y + 44

    def home(self, width):
        frame = self.new_frame("home", width)
        margin = self.header(frame, width)
        inner = width - 2 * margin
        desktop = width >= 1200
        if desktop:
            self.text(frame, "Software Engineer · Cairo, Egypt", margin, 145, 700, 18, RUST, "Medium")
            self.text(frame, "Ayman Ashraf\nMounir", margin, 202, 760, 80, TEXT, "Bold")
            self.text(frame, "I build backend systems and complete software products, from architecture to production.", margin, 448, 620, 22, MUTED)
            self.button(frame, "Explore my work", margin, 574, 190, target="projects")
            self.button(frame, "Download CV", margin + 210, 574, 174, False, url=CV_URL)
            self.image(frame, "portfolio-hero", 962, 163, 360, 480)
            y = 752
        else:
            self.text(frame, "Software Engineer, Backend Focused", margin, 133, inner, 15, FOCUS, "Medium")
            _, title = self.text(frame, "Ayman Ashraf\nMounir", margin, 178, inner, 60 if width >= 700 else 46, TEXT, "Bold")
            y = 178 + title["height"] + 26
            _, body = self.text(frame, "I build backend systems and complete software products, from architecture to production.", margin, y, inner, 20 if width >= 700 else 18, MUTED)
            y += body["height"] + 30
            self.button(frame, "View projects", margin, y, 156, target="projects")
            self.button(frame, "Download CV", margin + 176, y, 166, False, url=CV_URL)
            y += 76
            self.text(frame, "Cairo, Egypt", margin, y, inner, 14, MUTED)
            portrait_w = 300 if width >= 700 else 260
            portrait_h = portrait_w * 4 / 3
            self.image(frame, "portfolio-hero", margin + (inner - portrait_w) / 2, y + 45, portrait_w, portrait_h)
            y += portrait_h + 120
        self.text(frame, "Selected work", margin, y, inner, 36 if desktop else 34, TEXT, "SemiBold")
        y += 82
        self.text(frame, "Products, client platforms and public code.", margin, y, inner, 18, MUTED)
        y += 64
        if desktop:
            a = self.project_card(frame, PROJECTS[0], margin, y, 620, 300)
            b = self.project_card(frame, PROJECTS[1], margin + 660, y, 620, 300)
            y = max(a, b) + 48
            for project in [PROJECTS[7], PROJECTS[3]]:
                self.image(frame, project["slug"], margin, y, 315, 177)
                self.text(frame, project["title"], margin + 355, y + 12, 760, 28, TEXT, "SemiBold")
                self.text(frame, project["summary"], margin + 355, y + 68, 760, 18, MUTED)
                self.nav_link(frame, "Read case study", margin + 355, y + 133, 180, "project:" + project["slug"])
                y += 215
        else:
            if width >= 700:
                card_w = (inner - 28) / 2
                a = self.project_card(frame, PROJECTS[0], margin, y, card_w, 210)
                b = self.project_card(frame, PROJECTS[1], margin + card_w + 28, y, card_w, 210)
                y = max(a, b) + 60
            else:
                for project in PROJECTS[:2]:
                    y = self.project_card(frame, project, margin, y, inner, 230) + 45
            for project in [PROJECTS[7], PROJECTS[3]]:
                self.text(frame, project["title"], margin, y, inner, 25, TEXT, "SemiBold")
                _, box = self.text(frame, project["summary"], margin, y + 46, inner, 17, MUTED)
                y += 46 + box["height"] + 15
                self.nav_link(frame, "Read case study", margin, y, 180, "project:" + project["slug"])
                y += 70
        self.button(frame, "All projects", margin, y + 4, 172, False, target="projects")
        y += 135
        self.divider(frame, margin, y, inner)
        y += 65
        for title, body in [("Backend engineering", "Java, Spring Boot and reliable APIs"), ("Cloud-native products", "Multi-tenancy and serverless delivery"), ("Full-stack execution", "Requirements through product delivery")]:
            self.text(frame, title, margin, y, inner, 22, TEXT, "SemiBold")
            self.text(frame, body, margin, y + 43, inner, 16, MUTED)
            y += 105
        y += 30
        self.text(frame, "Experience", margin, y, 350 if desktop else inner, 40 if desktop else 34, TEXT, "SemiBold")
        if desktop:
            self.text(frame, "Backend systems, product delivery and technical evaluation.", margin, y + 76, 315, 21, MUTED)
            y = self.career_block(frame, margin + 460, y + 5, inner - 460) + 40
        else:
            y = self.career_block(frame, margin, y + 80, inner, compact=width < 700) + 40
        self.text(frame, "Education", margin, y, inner, 34, TEXT, "SemiBold")
        y += 70
        _, box = self.text(frame, "Bachelor's Degree in Computer Science\nFaculty of Computers and Artificial Intelligence\nCairo University", margin, y, inner, 22 if desktop else 19, TEXT)
        y += box["height"] + 16
        self.text(frame, "September 2021 to July 2025", margin, y, inner, 16, FOCUS)
        y += 108
        self.text(frame, "Technical strengths", margin, y, inner, 36 if desktop else 32, TEXT, "SemiBold")
        y = self.skill_block(frame, margin, y + 84, inner, 2 if width >= 700 else 1) + 48
        self.text(frame, "Certifications and participation", margin, y, inner, 32 if desktop else 28, TEXT, "SemiBold")
        y += 88 if desktop else 120
        for title, issuer, date in CERTS:
            _, box = self.text(frame, title, margin, y, inner, 21 if desktop else 18, TEXT, "Medium")
            y += box["height"] + 8
            _, box = self.text(frame, issuer + " / " + date, margin, y, inner, 15, MUTED)
            y += box["height"] + 30
        y += 55
        self.divider(frame, margin, y, inner)
        y += 64
        _, box = self.text(frame, "Have a product or\nengineering role in mind?", margin, y, inner, 46 if desktop else 32, TEXT, "SemiBold")
        y += box["height"] + 28
        self.button(frame, "Let's talk", margin, y, 156, target="contact")
        self.button(frame, "Download CV", margin + 176, y, 166, False, url=CV_URL)
        self.footer(frame, width, y + 132)
        return frame

    def listing(self, width, filter_name="All projects"):
        slug = "projects" if filter_name == "All projects" else "filter-products" if filter_name == "Products & Client Work" else "filter-public"
        frame = self.new_frame(slug, width, "route" if slug == "projects" else "state")
        margin = self.header(frame, width, "projects")
        inner = width - 2 * margin
        self.text(frame, "Projects", margin, 144, inner, 68 if width >= 1200 else 48, TEXT, "Bold")
        self.text(frame, "Products, client work and public engineering projects.", margin, 260 if width >= 1200 else 235, inner, 20 if width >= 700 else 18, MUTED)
        y = 340 if width >= 1200 else 328
        filters = [("All projects", "projects", 142), ("Products & Client Work", "filter-products", 213), ("Public Repositories", "filter-public", 190)]
        if width < 700:
            filters = [("All", "projects", 64), ("Client work", "filter-products", 122), ("Public code", "filter-public", 128)]
        x = margin
        for label, target, span in filters:
            chosen = target == slug
            ident, _ = self.node("frame", "Filter: " + label, x, y, span, 48, parent=frame,
                                  props={"fill": RUST if chosen else PAPER, "cornerRadius": 24, "stroke": RUST if chosen else LINE, "strokeWeight": 1})
            self.text(ident, label, 15, 11, span - 24, 14, PAPER if chosen else MUTED, "Medium")
            self.links.append((ident, target, self.current_width))
            x += span + 10
        y += 85
        shown = PROJECTS if filter_name == "All projects" else [p for p in PROJECTS if p["category"] == filter_name]
        self.text(frame, str(len(shown)) + " projects", margin, y, inner, 14, MUTED)
        y += 50
        columns = 3 if width >= 1200 else 2 if width >= 700 else 1
        gap = 34 if width >= 1200 else 26
        card_width = (inner - (columns - 1) * gap) / columns
        visual = [p for p in shown if self.image_source(p["slug"])]
        text_only = [p for p in shown if not self.image_source(p["slug"])]
        for start in range(0, len(visual), columns):
            ends = []
            for i, project in enumerate(visual[start:start + columns]):
                ends.append(self.project_card(frame, project, margin + i * (card_width + gap), y, card_width, 224 if width >= 1200 else 210))
            y = max(ends) + 58
        for project in text_only:
            y = self.project_card(frame, project, margin, y, inner, 0) + 35
        self.footer(frame, width, y + 20)
        return frame

    def case(self, width, project):
        frame = self.new_frame("project:" + project["slug"], width)
        margin = self.header(frame, width, "projects")
        inner = width - margin * 2
        desktop = width >= 1200
        self.nav_link(frame, "All projects", margin, 111, 160, "projects")
        self.text(frame, project["kind"], margin, 177, inner if not desktop else 600, 16, project["accent"], "Medium")
        _, title = self.text(frame, project["title"], margin, 220, 620 if desktop else inner, 60 if desktop else 46 if width >= 700 else 38, TEXT, "Bold")
        y = 220 + title["height"] + 20
        _, box = self.text(frame, project["summary"], margin, y, 515 if desktop else inner, 21 if desktop else 18, MUTED)
        y += box["height"] + 25
        self.text(frame, project["status"], margin, y, 520 if desktop else inner, 14, project["accent"], "Medium")
        y += 52
        if project.get("live"):
            self.button(frame, "Visit website", margin, y, 166, url=project["live"])
        if project.get("github"):
            self.button(frame, "View public code" if project["category"] == "Public Repositories" else "Public showcase", margin + ((178 if width < 700 else 188) if project.get("live") else 0), y, 164 if width < 700 else 172, not project.get("live"), url=project["github"])
        y += 82
        if desktop and self.image_source(project["slug"]):
            self.image(frame, project["slug"], 770, 180, 590, 410, True)
            y = max(y, 710)
        elif self.image_source(project["slug"]):
            self.image(frame, project["slug"], margin, y, inner, 365 if width >= 700 else 235, True)
            y += (365 if width >= 700 else 235) + 80
        else:
            y += 35
        self.divider(frame, margin, y, inner)
        y += 72
        if desktop:
            sidebar, _ = self.node("frame", "Case study section navigation", margin, y, 210, 430, parent=frame, props={"fill": PAPER})
            content_x, content_w = margin + 310, inner - 310
            anchors = []
        else:
            content_x, content_w = margin, inner
            sidebar, anchors = None, []
        for label, copy in [("Overview", project["overview"]), ("My contribution", project.get("role"))]:
            if not copy:
                continue
            heading, _ = self.text(frame, label, content_x, y, content_w, 32 if desktop else 28, TEXT, "SemiBold")
            anchors.append((label, heading))
            y += 62
            clean = copy.replace(", as described in the supplied CV", "").replace(", as described in the CV", "")
            _, box = self.text(frame, clean, content_x, y, content_w, 20 if desktop else 18, MUTED)
            y += box["height"] + 62
        self.text(frame, "Product capabilities", content_x, y, content_w, 31 if desktop else 27, TEXT, "SemiBold")
        y += 68
        for feature in project["features"]:
            self.rect(frame, "Feature marker", content_x, y + 8, 6, 6, project["accent"], 3)
            _, box = self.text(frame, feature, content_x + 22, y, content_w - 22, 20 if desktop else 18, TEXT)
            y += box["height"] + 21
        y += 45
        heading, box = self.text(frame, project["challenge"], content_x, y, content_w, 32 if desktop else 28, TEXT, "SemiBold")
        anchors.append(("Engineering", heading))
        y += box["height"] + 25
        _, box = self.text(frame, project["engineering"], content_x, y, content_w, 20 if desktop else 18, MUTED)
        y += box["height"] + 70
        heading, _ = self.text(frame, "Technical stack", content_x, y, content_w, 32 if desktop else 28, TEXT, "SemiBold")
        anchors.append(("Technical stack", heading))
        y += 70
        tx = content_x
        for stack in project["stack"]:
            tag_width = max(88, min(content_w, len(stack) * 8 + 28))
            if tx + tag_width > content_x + content_w:
                tx, y = content_x, y + 59
            tag, _ = self.node("frame", stack, tx, y, tag_width, 42, parent=frame, props={"fill": SURFACE, "cornerRadius": 8, "stroke": LINE, "strokeWeight": 1})
            self.text(tag, stack, 14, 10, tag_width - 20, 14, TEXT)
            tx += tag_width + 12
        y += 110
        self.text(frame, "Testing and reliability", content_x, y, content_w, 32 if desktop else 28, TEXT, "SemiBold")
        y += 66
        _, box = self.text(frame, project["validation"], content_x, y, content_w, 18, MUTED)
        y += box["height"] + 75
        if project.get("capture"):
            capture = DESIGN / "assets" / "captures" / (project["capture"] + ".png")
            if capture.exists():
                heading, _ = self.text(frame, "Public presentation", content_x, y, content_w, 32 if desktop else 28, TEXT, "SemiBold")
                anchors.append(("Selected visual", heading))
                y += 76
                holder, _ = self.node("frame", "Genuine public capture", content_x, y, content_w, content_w * 1000 / 1440, parent=frame, props={"fill": SURFACE, "clip": True, "cornerRadius": 12})
                self.mcp.command("image.place", {"path": str(capture), "parent": holder, "width": content_w, "height": content_w * 1000 / 1440, "mode": "fit"})
                if project["slug"] == "helixtra":
                    self.links.append((holder, "gallery-helixtra", self.current_width))
                y += content_w * 1000 / 1440 + 20
                _, box = self.text(frame, project["caption"], content_x, y, content_w, 13, MUTED)
                y += box["height"] + 60
        if sidebar:
            for i, (label, anchor) in enumerate(anchors):
                item, _ = self.node("frame", "Jump to " + label, 0, i * 58, 205, 48, parent=sidebar, props={"fill": PAPER})
                self.text(item, label, 0, 13, 205, 15, MUTED)
                self.mcp.command("proto.interaction.add", {"id": item, "trigger": {"type": "onClick"}, "action": {"type": "scrollTo", "dest": anchor, "offset": [0, 100]}})
        self.divider(frame, margin, y, inner)
        y += 55
        self.text(frame, "Explore more work", margin, y, inner, 32, TEXT, "SemiBold")
        y += 74
        index = PROJECTS.index(project)
        previous, following = PROJECTS[(index - 1) % len(PROJECTS)], PROJECTS[(index + 1) % len(PROJECTS)]
        self.nav_link(frame, "Previous: " + previous["title"], margin, y, inner if width < 700 else inner / 2 - 30, "project:" + previous["slug"])
        self.nav_link(frame, "Next: " + following["title"], margin if width < 700 else margin + inner / 2 + 30, y + 62 if width < 700 else y, inner if width < 700 else inner / 2 - 30, "project:" + following["slug"])
        self.footer(frame, width, y + (140 if width < 700 else 100))
        return frame

    def text_page(self, slug, width):
        frame = self.new_frame(slug, width)
        margin = self.header(frame, width, slug)
        inner, desktop = width - 2 * margin, width >= 1200
        title = {"about": "About Ayman", "experience": "Experience", "resume": "Resume", "contact": "Let's talk", "404": "Page not found"}[slug]
        self.text(frame, title, margin, 150, inner, 68 if desktop else 46, TEXT, "Bold")
        y = 292 if desktop else 270
        if slug == "about":
            _, box = self.text(frame, "Backend focus.\nComplete product delivery.", margin, y, 720 if desktop else inner, 38 if desktop else 29, TEXT, "SemiBold")
            y += box["height"] + 32
            _, box = self.text(frame, "I'm Ayman Ashraf Mounir, a Cairo-based Software Engineer. My work spans Java backend systems, cloud-native SaaS platforms and full-stack applications, from requirements and architecture to implementation, testing and deployment.", margin, y, 780 if desktop else inner, 21 if desktop else 18, MUTED)
            y += box["height"] + 46
            _, box = self.text(frame, "I also contribute to AI evaluation and benchmarking, designing technical tasks and verification criteria that test reasoning, correctness and reliability.", margin, y, 780 if desktop else inner, 21 if desktop else 18, MUTED)
            y += box["height"] + 80
            portrait_w = min(inner, 360)
            portrait_h = portrait_w * 4 / 3
            self.image(frame, "portfolio-hero", margin, y, portrait_w, portrait_h)
            y += portrait_h + 80
            self.text(frame, "Technical strengths", margin, y, inner, 34, TEXT, "SemiBold")
            y = self.skill_block(frame, margin, y + 82, inner, 2 if width >= 700 else 1) + 35
            self.button(frame, "View projects", margin, y, 164, target="projects")
            self.button(frame, "Contact", margin + 186, y, 150, False, target="contact")
            y += 130
        elif slug == "experience":
            _, box = self.text(frame, "Backend engineering, product delivery and technical evaluation. Overlapping roles are shown with their original dates.", margin, y, inner, 21 if desktop else 18, MUTED)
            y = self.career_block(frame, margin, y + box["height"] + 70, min(inner, 980), width < 700)
            self.button(frame, "Download CV", margin, y + 22, 172, url=CV_URL)
            y += 150
        elif slug == "resume":
            _, box = self.text(frame, "Ayman Ashraf Mounir", margin, y, inner, 34, TEXT, "SemiBold")
            y += box["height"] + 20
            self.text(frame, "Software Engineer / Cairo, Egypt", margin, y, inner, 18, FOCUS)
            self.button(frame, "Download original CV", margin, y + 60, 218, url=CV_URL)
            y += 155
            _, box = self.text(frame, "Software Engineer with experience building Java backend systems, serverless SaaS platforms and full-stack applications. Object-Oriented Design and SOLID principles, REST APIs, performance-focused refactoring and Agile/SCRUM collaboration.", margin, y, inner, 19 if desktop else 17, MUTED)
            y += box["height"] + 65
            self.text(frame, "Experience", margin, y, inner, 32, TEXT, "SemiBold")
            y = self.career_block(frame, margin, y + 72, inner, width < 700)
            self.text(frame, "Education", margin, y + 20, inner, 32, TEXT, "SemiBold")
            y += 88
            _, box = self.text(frame, "Bachelor's Degree in Computer Science\nFaculty of Computers and Artificial Intelligence, Cairo University\nSeptember 2021 to July 2025", margin, y, inner, 19 if desktop else 17, MUTED)
            y += box["height"] + 70
            self.text(frame, "Technical skills", margin, y, inner, 32, TEXT, "SemiBold")
            y = self.skill_block(frame, margin, y + 75, inner, 2 if width >= 700 else 1) + 50
            self.text(frame, "Project experience", margin, y, inner, 32, TEXT, "SemiBold")
            y += 70
            cv_projects = [PROJECTS[i] for i in [0, 1, 6, 7, 9]] + [{"title": "Hala Kazim", "summary": "Retreat booking platform built with Next.js, TypeScript, Prisma and PostgreSQL."}] + [PROJECTS[10], PROJECTS[11]]
            for project in cv_projects:
                self.text(frame, project["title"], margin, y, inner, 21, TEXT, "SemiBold")
                _, box = self.text(frame, project["summary"], margin, y + 43, inner, 17, MUTED)
                y += 43 + box["height"] + 35
            self.text(frame, "Certifications and achievement", margin, y + 25, inner, 30, TEXT, "SemiBold")
            y += 112
            for title, issuer, date in CERTS:
                _, box = self.text(frame, title + "\n" + issuer + " / " + date, margin, y, inner, 18, MUTED)
                y += box["height"] + 25
            y += 45
        elif slug == "contact":
            _, box = self.text(frame, "Have a product, backend challenge or engineering role in mind?", margin, y, min(inner, 960), 36 if desktop else 28, TEXT, "SemiBold")
            y += box["height"] + 35
            _, box = self.text(frame, "Email is the direct way to reach me. You can also inspect my public work and professional profile.", margin, y, min(inner, 820), 21 if desktop else 18, MUTED)
            y += box["height"] + 75
            self.text(frame, "Professional email", margin, y, inner, 16, FOCUS)
            _, box = self.text(frame, DATA["identity"]["email"], margin, y + 40, inner, 36 if desktop else 22, TEXT, "Medium")
            y += box["height"] + 82
            self.button(frame, "Send an email", margin, y, 172, url="mailto:" + DATA["identity"]["email"])
            y += 115
            self.divider(frame, margin, y, inner)
            y += 46
            self.button(frame, "GitHub", margin, y, 156, False, url=DATA["identity"]["github"])
            self.button(frame, "LinkedIn", margin + 176, y, 166, False, url=DATA["identity"]["linkedin"])
            self.text(frame, "Cairo, Egypt", margin, y + 105, inner, 18, MUTED)
            y += 220
        else:
            self.text(frame, "404", margin, y, inner, 180 if desktop else 110, RUST, "Bold")
            y += 270 if desktop else 190
            _, box = self.text(frame, "This address doesn't point to a page. Explore the projects or return to the portfolio.", margin, y, min(inner, 820), 23 if desktop else 19, MUTED)
            y += box["height"] + 36
            self.button(frame, "Return home", margin, y, 160, target="home")
            self.button(frame, "View projects", margin + 180, y, 162, False, target="projects")
            y += 180
        self.footer(frame, width, y + 40)
        return frame

    def menu(self, width):
        frame = self.new_frame("menu-open", width, "state")
        margin = 40 if width >= 700 else 24
        self.text(frame, "Ayman Ashraf", margin, 35, width - margin * 2, 22, TEXT, "SemiBold")
        self.nav_link(frame, "Close", width - margin - 70, 25, 70, "home")
        y = 150
        for label, target in [("Projects", "projects"), ("About", "about"), ("Experience", "experience"), ("Resume", "resume"), ("Contact", "contact")]:
            ident, _ = self.node("frame", label, margin, y, width - margin * 2, 68, parent=frame, props={"fill": PAPER})
            self.text(ident, label, 0, 5, width - margin * 2, 36, TEXT, "Medium")
            self.links.append((ident, target, self.current_width))
            y += 98
        self.button(frame, "Download CV", margin, y + 10, 174, url=CV_URL)
        self.text(frame, "Cairo, Egypt", margin, y + 110, width - margin * 2, 16, MUTED)
        self.mcp.command("node.set", {"ids": [frame], "height": max(y + 190, 844)})
        return frame

    def gallery(self, width):
        frame = self.new_frame("gallery-helixtra", width, "state")
        margin = 80 if width >= 1200 else 40 if width >= 700 else 24
        inner = width - margin * 2
        self.text(frame, "Helixtra / Public presentation", margin, 45, inner - 75, 22 if width >= 700 else 18, TEXT, "SemiBold")
        self.nav_link(frame, "Close", width - margin - 65, 35, 65, "project:helixtra")
        shot = DESIGN / "assets" / "captures" / "helixtra-marketing.png"
        height = inner * 1000 / 1440
        holder, _ = self.node("frame", "Enlarged genuine public marketing capture", margin, 140, inner, height, parent=frame, props={"fill": SURFACE, "clip": True, "cornerRadius": 12})
        self.mcp.command("image.place", {"path": str(shot), "parent": holder, "width": inner, "height": height, "mode": "fit"})
        self.text(frame, "Public marketing page. This is not an authenticated product screen.", margin, 170 + height, inner, 14, MUTED)
        self.mcp.command("node.set", {"ids": [frame], "height": max(270 + height, 844)})
        return frame

    def export_screens(self):
        directory = DESIGN / "screens"
        directory.mkdir(exist_ok=True)
        inspections = []
        for frame in self.frames:
            native = self.mcp.tool("get_node", {"id": frame["id"], "depth": 20})
            frame["height"] = native["height"]
            slug = frame["slug"].replace(":", "-")
            path = directory / (slug + "-" + str(frame["width"]) + ".png")
            self.mcp.tool("export", {"ids": [frame["id"]], "path": str(path), "format": "png"})
            frame["export"] = str(path.relative_to(ROOT)).replace("\\", "/")
            inspections.append({"frame": frame, "node": native})
            print("Exported " + slug + " " + str(frame["width"]), flush=True)
        self.mcp.tool("export", {"ids": [self.foundation_id], "path": str(directory / "foundations.png"), "format": "png"})
        (DESIGN / "screen-inspection.json").write_text(json.dumps(inspections), encoding="utf-8")
        (DESIGN / "screen-manifest.json").write_text(json.dumps(self.frames, indent=2), encoding="utf-8")

    def finish(self):
        by_key = {(f["width"], f["slug"]): f["id"] for f in self.frames}
        doc = self.mcp.tool("inspect_document", {"depth": 0, "allPages": True})
        for ident, target, width in self.links:
            if target.startswith("external:"):
                url = DATA["identity"][target.split(":")[1]]
                self.mcp.command("proto.interaction.add", {"id": ident, "trigger": {"type": "onClick"}, "action": {"type": "openUrl", "url": url}})
                continue
            destination = by_key.get((width, target))
            if destination is None:
                raise RuntimeError("Missing navigation destination " + target)
            self.mcp.command("proto.interaction.add", {"id": ident, "dest": destination})
        self.mcp.command("page.select", {"id": self.pages[1440]})
        self.mcp.tool("select", {"ids": [by_key[(1440, "home")]]})
        self.mcp.command("view.zoomSelection")
        self.mcp.tool("save_file", {"path": str(DESIGN / "ayman-portfolio-v2.figcraft")})
        self.export_screens()

    def run(self, pilot=False):
        self.foundation()
        for width in ([1440, 390] if pilot else [1440, 768, 390]):
            self.mcp.command("page.select", {"id": self.pages[width]})
            home = self.home(width)
            self.mcp.command("proto.flow.add", {"start": home, "name": "Portfolio " + str(width)})
            print("Created homepage " + str(width), flush=True)
            if not pilot:
                self.listing(width)
                for project in PROJECTS:
                    self.case(width, project)
                    print("Created " + project["slug"] + " " + str(width), flush=True)
                for slug in ["about", "experience", "resume", "contact", "404"]:
                    self.text_page(slug, width)
                self.listing(width, "Products & Client Work")
                self.listing(width, "Public Repositories")
                if width < 1200:
                    self.menu(width)
                self.gallery(width)
            self.mcp.tool("save_file", {"path": str(DESIGN / ("pilot.figcraft" if pilot else "ayman-portfolio-v2.figcraft"))})
        if not pilot:
            self.finish()
        else:
            (DESIGN / "pilot-frames.json").write_text(json.dumps(self.frames, indent=2), encoding="utf-8")
            for frame in self.frames:
                path = DESIGN / "screens" / ("home-" + str(frame["width"]) + ".png")
                path.parent.mkdir(exist_ok=True)
                self.mcp.tool("export", {"ids": [frame["id"]], "path": str(path), "format": "png"})
                print("Exported " + str(path), flush=True)
        self.mcp.save_log(DESIGN / ("pilot-mcp-calls.json" if pilot else "figcraft-mcp-calls.json"))


if __name__ == "__main__":
    screens = Screens()
    try:
        screens.run(pilot="--pilot" in sys.argv)
    finally:
        screens.mcp.close()
