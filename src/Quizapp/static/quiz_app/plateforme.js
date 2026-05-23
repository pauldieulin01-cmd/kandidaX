<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Plateforme Concours Université</title>
<style>
/* RESET & BODY */
* {margin:0; padding:0; box-sizing:border-box;}
body {font-family: Arial, sans-serif; line-height:1.6; background:#f0f2f5; color:#333;}

/* HEADER */
.header {
    display:flex; justify-content:space-between; align-items:center;
    padding:15px 40px; background:white; box-shadow:0 2px 8px rgba(0,0,0,0.1);
}
.header .logo {font-size:26px; font-weight:bold;}
.header nav a {
    margin-left:15px; text-decoration:none; color:#333; font-weight:500;
    transition: all 0.3s ease;
}
.header nav a:hover {color:#2563eb; transform:scale(1.05);}
.btn, .btn-primary {padding:12px 20px; border-radius:8px; border:none; cursor:pointer; font-size:16px; text-decoration:none;}
.btn-primary {background:#2563eb; color:white; box-shadow:0 4px #1a3a8a;}
.btn-primary:active {top:2px; box-shadow:0 0 #1a3a8a;}
.btn-secondary {background:transparent; border:2px solid white; color:white; margin-left:10px;}
.arrow {transition:transform 0.3s;} .arrow.rotate {transform:rotate(180deg);}

/* BACKDROP & POPUP */
.backdrop {display:none; position:fixed; inset:0; background:rgba(0,0,0,0.55); z-index:900;}
.backdrop.active {display:block;}
.toggle-section {
    display:none; position:fixed; top:50%; left:50%; width:90%; max-width:400px;
    transform:translate(-50%,-50%) scale(0.8); background:white; padding:30px;
    border-radius:18px; box-shadow:0 20px 40px rgba(0,0,0,0.35); z-index:1000; opacity:0;
    transition: all 0.35s ease;
}
.toggle-section.active {display:block; opacity:1; transform:translate(-50%,-50%) scale(1);}

/* HERO */
.hero {
    position:relative; height:70vh; background:url("etudiant.avif") center/cover no-repeat;
    display:flex; align-items:center; justify-content:center; color:white; text-align:center;
}
.hero .overlay {position:absolute; inset:0; background:rgba(0,0,0,0.6);}
.hero-content {position:relative; max-width:900px; padding:20px; animation:heroAppear 1s ease forwards;}
.hero-content h1 {font-size:36px;}
.hero-content p {font-size:20px; margin:20px 0;}
.actions a {margin:0 10px;}

/* ANIMATION HERO */
@keyframes heroAppear {from {opacity:0; transform:translateY(40px);} to {opacity:1; transform:translateY(0);}}

/* SECTIONS */
.features, .subjects, .cta {padding:60px 40px; text-align:center;}
.cards {display:flex; gap:20px; justify-content:center; flex-wrap:wrap;}
.card {background:#f3f4f6; padding:25px; width:300px; border-radius:10px;}
.subjects {background:#2563eb; color:white;}
.subjects-list {list-style:none; display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:15px; font-size:22px;}
.cta a {margin-top:20px; display:inline-block;}

/* SIGNUP FORM */
.signup {background:url("etudiant3.avif") center/cover no-repeat; padding:80px 20px; text-align:center;}
.signup-form {max-width:500px; margin:auto; background:white; padding:40px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.1);}
.signup-form h2 {font-size:30px; margin-bottom:10px;}
.signup-form p {font-size:18px; margin-bottom:20px; color:#555;}
.form-group {margin-bottom:20px; text-align:left;}
.form-group label {display:block; font-weight:bold; margin-bottom:8px;}
.form-group input, .form-group select {
    width:100%; padding:12px; font-size:16px; border-radius:8px; border:1px solid #ccc;
}
.form-group input:focus, .form-group select:focus {outline:none; border-color:#2563eb;}

/* FOOTER */
.footer {background:#111; color:white; text-align:center; padding:25px;}
.footer a {color:white; margin:0 5px; text-decoration:none;}
.footer a:hover {text-decoration:underline;}

/* AUTH FORM */
.auth-hero {position:relative; height:100vh; background:url("etudiant3.avif") center/cover no-repeat; display:flex; align-items:center; justify-content:center;}
.auth-overlay {position:absolute; inset:0; background:rgba(0,0,0,0.6);}
.auth-card {position:relative; background:white; padding:40px; width:380px; border-radius:16px; text-align:center; z-index:2; box-shadow:0 20px 40px rgba(0,0,0,0.3);}
.auth-card h2 {margin-bottom:10px;}
.auth-card input {width:100%; padding:14px; margin-bottom:15px; border-radius:10px; border:1px solid #d1d5db; font-size:16px;}
.auth-card input:focus {border-color:#2563eb; outline:none;}
.auth-links a {color:#2563eb; font-weight:bold; text-decoration:none;}
.auth-links a:hover {text-decoration:underline;}

/* QUESTIONS */
.container {max-width:900px; margin:50px auto; background:white; border-radius:15px; padding:30px; box-shadow:0 5px 15px rgba(0,0,0,0.1); text-align:center;}
.question-header {display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;}
.progress-container {background:#ddd; border-radius:10px; height:12px; margin-bottom:20px;}
.progress-bar {height:12px; border-radius:10px; background:#4CAF50; width:0; transition:width 0.3s;}
.answers {display:flex; flex-direction:column; gap:10px; align-items:center;}
.answer {padding:12px 20px; border:2px solid #ccc; border-radius:12px; cursor:pointer; width:70%; transition:all 0.3s; text-align:center;}
.answer:hover {border-color:#4CAF50; background:#f1f8f5;}
.answer.correct {border-color:#4CAF50; background:#c8e6c9;}
.answer.incorrect {border-color:#f44336; background:#ffcdd2;}
.feedback {margin-top:15px; font-weight:bold; font-size:1.1em;}
button {padding:12px 20px; border:none; border-radius:10px; cursor:pointer; font-weight:bold; transition:all 0.2s;}
button:hover {transform:translateY(-2px);}
.btn-danger {background:#f44336; color:white;}
/* ======================== */
/* MEDIA QUERIES RESPONSIVE */
/* ======================== */

/* Petits écrans (smartphones < 768px) */
@media (max-width: 768px) {
    .header {flex-direction: column; align-items: flex-start; padding: 10px 20px;}
    .header nav {display: none; flex-direction: column; width: 100%; margin-top: 10px;}
    .header nav a {margin: 10px 0;}
    .menu-toggle {display:block; cursor:pointer; font-size:24px; color:#333;}
    
    .hero-content h1 {font-size:28px;}
    .hero-content p {font-size:18px;}
    
    .cards {flex-direction: column; align-items: center;}
    .card {width:90%; margin-bottom:15px;}
    
    .subjects-list {grid-template-columns:1fr;}
    
    .signup-form, .auth-card, .container {width:90%; padding:25px;}
    .answers .answer {width:90%;}
}

/* Très petits écrans (mobiles < 480px) */
@media (max-width: 480px) {
    .hero-content h1 {font-size:24px;}
    .hero-content p {font-size:16px;}
    .btn, .btn-primary {padding:10px 15px; font-size:14px;}
}
</style>
</head>
<body>

<!-- HEADER -->
<header class="header">
   <div class="logo">LOGO DU SITE</div>
<div class="menu-toggle">☰</div>
<nav>
    <a href="#">Accueil</a>
    <a href="#">Cours</a>
    <a href="#" data-target="about">À propos ⬇</a>
    <a href="#" data-target="contact">Contact ⬇</a>
    <a href="connexion.html" class="btn">Connexion</a>
    <a href="inscription.html" class="btn-primary">S’inscrire</a>
</nav>
</header>

<!-- BACKDROP -->
<div id="backdrop" class="backdrop"></div>

<!-- POPUPS -->
<section id="about" class="toggle-section">
    <h2>À propos de la plateforme</h2>
    <p>Nous aidons les étudiants haïtiens à réussir les concours d’entrée aux universités publiques grâce à des tests, cours ciblés et un suivi intelligent.</p>
</section>

<section id="contact" class="toggle-section">
    <h2>Contactez-nous</h2>
    <p>📧 Email : contact@concours.ht</p>
    <p>📞 Téléphone : +509 00 00 0000</p>
</section>

<!-- HERO -->
<section class="hero">
    <div class="overlay"></div>
    <div class="hero-content">
        <h1>La plateforme de référence pour réussir les concours universitaires</h1>
        <p>Préparez efficacement votre concours d’entrée à l’université.</p>
        <div class="actions">
            <a href="connexion.html" class="btn-primary">Commencer le test</a>
            <a href="tableau_bord.html" class="btn-primary">Découvrir les cours</a>
        </div>
    </div>
</section>

<!-- FEATURES -->
<section class="features">
    <h2>Pourquoi utiliser notre plateforme ?</h2>
    <div class="cards">
        <div class="card">
            <h3>📘 Tests interactifs</h3>
            <p>Entraînez-vous avec des questions inspirées des concours officiels et des sujets passés.</p>
        </div>
        <div class="card">
            <h3>📊 Suivi de progression</h3>
            <p>Analysez vos résultats et améliorez progressivement vos performances.</p>
        </div>
        <div class="card">
            <h3>🧭 Conseils d’orientation</h3>
            <p>Recevez des conseils adaptés pour choisir votre filière universitaire.</p>
        </div>
    </div>
</section>

<!-- MATIÈRES -->
<section class="subjects">
    <h2>Matières disponibles</h2>
    <ul class="subjects-list">
        <li>Mathématiques</li>
        <li>Physique</li>
        <li>Chimie</li>
        <li>SVT</li>
        <li>Français</li>
        <li>Culture générale</li>
        <li>Philosophie</li>
    </ul>
</section>

<!-- CTA -->
<section class="cta">
    <h2>Commencez votre préparation dès aujourd’hui</h2>
    <a href="inscription.html" class="btn-primary">S’inscrire gratuitement</a>
</section>

<!-- FOOTER -->
<footer class="footer">
    <a href="#">Accueil</a>
    <a href="#">Cours</a>
    <a href="#" data-target="about">À propos</a>
    <a href="#" data-target="contact">Contact</a>
    <a href="#">Conditions générales</a>
    <a href="#">Politique de confidentialité</a>
    <p>© 2026 — Plateforme Concours Université</p>
</footer>

<!-- JS -->
<script>
document.querySelectorAll('[data-target]').forEach(btn=>{
    btn.addEventListener('click',()=>{
        const target = document.getElementById(btn.dataset.target);
        target.classList.add('active');
        document.getElementById('backdrop').classList.add('active');
    });
});
document.getElementById('backdrop').addEventListener('click',()=>{
    document.querySelectorAll('.toggle-section').forEach(s=>s.classList.remove('active'));
    document.getElementById('backdrop').classList.remove('active');
});
const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('header nav');
menuToggle.addEventListener('click', ()=>{
    nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
});
</script>
</body>
</html>