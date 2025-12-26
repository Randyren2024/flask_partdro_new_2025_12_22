# Update `debug.html` to Tailwind CSS Architecture

I will refactor `debug.html` to align with the project's current architecture (Tailwind CSS, Base Template, Header/Footer).

## 1. Structure & Inheritance

* **Extend Base**: Change `debug.html` to extend `base.html` instead of being a standalone file. This ensures it inherits the global Tailwind config, Header, and Footer.

* **Blocks**: Move content into `{% block content %}` and scripts into `{% block scripts %}`.

## 2. UI/UX Redesign (Bootstrap -> Tailwind)

I will replace all Bootstrap 5 classes with Tailwind CSS utility classes, adhering to the project's "Tech" theme defined in `base.html`.

* **Layout**:

  * `container` -> `container mx-auto px-4 py-12`

  * `row/col` -> `grid grid-cols-1 lg:grid-cols-2 gap-8`

* **Components**:

  * **Cards**: `.tech-card` -> `.glass-card rounded-xl p-6` (using the class from `base.html`).

  * **Buttons**: `.btn-tech` -> `border border-cyberCyan text-cyberCyan hover:bg-cyberCyan hover:text-deepNavy transition-all px-6 py-2 rounded uppercase font-bold tracking-wider`.

  * **Inputs**: `.form-control` -> `w-full bg-darkCurrent/50 border border-white/10 rounded px-4 py-3 text-white focus:border-cyberCyan focus:outline-none focus:ring-1 focus:ring-cyberCyan transition-all`.

* **Tabs**:

  * Since `base.html` does not include Bootstrap JS, I will implement a lightweight **Vanilla JS Tab Switcher** to handle the switching between "Single Product", "CSV Import", and "AI Builder".

## 3. Functionality Preservation

* Ensure all Form IDs (`productForm`, `csvForm`) and Button IDs (`btnTranslate`, `btnGenerateLP`, `btnSaveLP`) remain unchanged so the existing JavaScript logic works seamlessly.

* Re-implement the "Loading Overlay" using Tailwind fixed positioning classes.

## 4. Verification

* I will verify the page renders correctly with the Header/Footer.

* I will verify the Tabs switch correctly.

* I will verify the forms still look good and are accessible.

