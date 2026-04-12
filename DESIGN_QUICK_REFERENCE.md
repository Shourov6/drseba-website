# Modern Healthcare Design System - Quick Reference

## Color Palette

```css
/* Primary Colors */
--primary-blue: #0A74DA
--primary-blue-dark: #0858a8
--primary-blue-light: #e3f2fd

/* Secondary Colors */
--secondary-green: #28A745
--secondary-green-dark: #1e7e34
--secondary-green-light: #d4edda

/* Neutral Colors */
--light-bg: #F5F7FA
--white: #FFFFFF
--dark-text: #1F2937
--muted-gray: #6B7280
--subtle-border: #E5E7EB

/* Effects */
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06)
--shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08)
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.1)

/* Timing */
--transition-fast: 0.2s ease
--transition-smooth: 0.3s ease

/* Spacing */
--border-radius-sm: 10px
--border-radius-md: 12px
--border-radius-lg: 16px
```

## Common Components

### Buttons
```html
<!-- Primary Button -->
<button class="btn btn-primary">Action</button>

<!-- Success Button -->
<button class="btn btn-success">Confirm</button>

<!-- Outline Button -->
<button class="btn btn-outline-primary">Secondary</button>

<!-- Pill Button -->
<button class="btn btn-pill">Rounded</button>

<!-- Small Button -->
<button class="btn btn-sm">Small</button>

<!-- Large Button -->
<button class="btn btn-lg">Large</button>
```

### Cards
```html
<!-- Standard Card -->
<div class="card">
    <div class="card-header">
        <h5>Header</h5>
    </div>
    <div class="card-body">
        Content here
    </div>
</div>

<!-- Selectable Card -->
<div class="card card-selectable selected">
    Content with checkmark
</div>
```

### Forms
```html
<!-- Text Input -->
<label class="form-label">Label</label>
<input type="text" class="form-control" placeholder="Enter text">

<!-- Select -->
<select class="form-select">
    <option>Option 1</option>
    <option>Option 2</option>
</select>

<!-- Checkbox -->
<div class="form-check">
    <input class="form-check-input" type="checkbox" id="check">
    <label class="form-check-label" for="check">Agree</label>
</div>
```

### Progress Indicator
```html
<div class="progress-indicator">
    <div class="progress-step">
        <div class="progress-step-number active">1</div>
        <div class="progress-step-label active">Step</div>
    </div>
    <div class="progress-connector active"></div>
    <div class="progress-step">
        <div class="progress-step-number completed">2</div>
        <div class="progress-step-label completed">Complete</div>
    </div>
</div>
```

### Toggle Group
```html
<div class="toggle-group">
    <button class="toggle-btn active">Option 1</button>
    <button class="toggle-btn">Option 2</button>
</div>
```

### Date Pills
```html
<div class="date-pills">
    <button class="date-pill selected">18 Apr</button>
    <button class="date-pill">19 Apr</button>
    <button class="date-pill">20 Apr</button>
</div>
```

### Hospital Cards
```html
<div class="hospital-cards">
    <div class="hospital-card card-selectable selected">
        <div class="hospital-name">Hospital Name</div>
        <div class="hospital-location">
            <i class="bi bi-geo-alt"></i>
            <span>Address</span>
        </div>
        <div class="hospital-distance">5 km away</div>
    </div>
</div>
```

### Doctor Info
```html
<div class="doctor-info">
    <img class="doctor-avatar" src="..." alt="Doctor">
    <div class="doctor-details">
        <h5>Dr. Name</h5>
        <div class="doctor-specialization">Cardiology</div>
        <div class="doctor-rating">
            <span class="stars">★★★★★</span>
            <span>(4.5)</span>
        </div>
        <div class="doctor-experience">
            <i class="bi bi-briefcase"></i>
            <span>15 years experience</span>
        </div>
    </div>
</div>
```

### Summary Section
```html
<div class="summary-section">
    <div class="summary-row">
        <span class="summary-label">Item:</span>
        <span class="summary-value">Value</span>
    </div>
    <div class="summary-row total">
        <span>Total:</span>
        <span class="text-primary">$100</span>
    </div>
</div>
```

### Contact Buttons
```html
<div class="contact-section">
    <div class="contact-title">Need Help?</div>
    <div class="contact-buttons">
        <a href="tel:..." class="contact-btn phone">
            <i class="bi bi-telephone"></i>
            <span>Call</span>
        </a>
        <a href="..." class="contact-btn whatsapp">
            <i class="bi bi-chat-dots"></i>
            <span>WhatsApp</span>
        </a>
    </div>
</div>
```

### Alerts
```html
<!-- Info Alert -->
<div class="alert alert-info">
    <i class="bi bi-info-circle"></i> Information message
</div>

<!-- Success Alert -->
<div class="alert alert-success">
    <i class="bi bi-check-circle"></i> Success message
</div>

<!-- Warning Alert -->
<div class="alert alert-warning">
    <i class="bi bi-exclamation-triangle"></i> Warning message
</div>

<!-- Error Alert -->
<div class="alert alert-danger">
    <i class="bi bi-x-circle"></i> Error message
</div>
```

## Utility Classes

### Text Color
```html
<span class="text-primary">Primary Blue</span>
<span class="text-success">Success Green</span>
<span class="text-muted">Muted Gray</span>
```

### Background Color
```html
<div class="bg-light">Light Background</div>
<div class="bg-primary-light">Primary Light</div>
<div class="bg-success-light">Success Light</div>
```

### Shadows
```html
<div class="shadow-sm">Subtle Shadow</div>
<div class="shadow-md">Medium Shadow</div>
<div class="shadow-lg">Large Shadow</div>
```

### Borders
```html
<div class="border-primary">Blue Border</div>
<div class="border-success">Green Border</div>
```

### Spacing (Margins & Padding)
```html
<!-- Margin Top -->
<div class="mt-0">No top margin</div>
<div class="mt-1">0.5rem</div>
<div class="mt-2">1rem</div>
<div class="mt-3">1.5rem</div>
<div class="mt-4">2rem</div>
<div class="mt-5">2.5rem</div>

<!-- Margin Bottom (same scale) -->
<div class="mb-1">0.5rem</div>
<div class="mb-2">1rem</div>
<!-- etc -->

<!-- Gap (for flex/grid) -->
<div class="gap-1">0.5rem gap</div>
<div class="gap-2">1rem gap</div>
<div class="gap-3">1.5rem gap</div>
<div class="gap-4">2rem gap</div>
```

### Border Radius
```html
<div class="rounded-lg">16px radius</div>
```

### Transitions
```html
<div class="smooth-transition">Smooth 0.3s ease</div>
```

## Common Patterns

### 2-Column Layout (Responsive)
```html
<div class="row">
    <div class="col-lg-8">
        <!-- Main content -->
    </div>
    <div class="col-lg-4">
        <!-- Sidebar -->
    </div>
</div>
```

### Sticky Sidebar
```html
<div class="card sticky-top" style="top: 20px;">
    <!-- Sidebar content -->
</div>
```

### Card with Header & Footer
```html
<div class="card">
    <div class="card-header">
        <h5>Title</h5>
    </div>
    <div class="card-body">
        Content
    </div>
    <div class="card-footer">
        Footer text
    </div>
</div>
```

### Icon + Text Button
```html
<button class="btn btn-primary btn-icon">
    <i class="bi bi-arrow-right"></i>
    <span>Action</span>
</button>
```

## Responsive Grid

```html
<!-- 4 Columns on Desktop, 2 on Tablet, 1 on Mobile -->
<div class="row g-3">
    <div class="col-lg-3 col-md-6 col-12">Card 1</div>
    <div class="col-lg-3 col-md-6 col-12">Card 2</div>
    <div class="col-lg-3 col-md-6 col-12">Card 3</div>
    <div class="col-lg-3 col-md-6 col-12">Card 4</div>
</div>
```

## Tips & Best Practices

✓ Always use CSS variables for colors  
✓ Use predefined border-radius values  
✓ Include hover states for interactive elements  
✓ Test responsive layouts on mobile  
✓ Use semantic color coding (green=success, blue=primary, red=error)  
✓ Maintain consistent padding/margins using utility classes  
✓ Use smooth transitions for better UX  
✓ Test contrast ratios for accessibility  

## Resources

- Color variables: All defined in `:root` of `modern-healthcare.css`
- Full documentation: See `DESIGN_SYSTEM.md`
- Bootstrap 5: Used for grid, responsive utilities
- Bootstrap Icons: Icon library (bi-*)
- Font families: Inter, Roboto, Poppins via Google Fonts
