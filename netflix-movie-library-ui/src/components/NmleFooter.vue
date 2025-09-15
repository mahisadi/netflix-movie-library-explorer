<template>
  <footer class="nmle-footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-section">
          <h3>Movie Library Explorer</h3>
          <p>Discover and explore your movie collection with powerful search capabilities.</p>
        </div>
        <div class="footer-section">
          <h4>Features</h4>
          <ul>
            <li>Advanced Search</li>
            <li>Smart Filtering</li>
            <li>Movie Details</li>
            <li>Collection Stats</li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>Technology</h4>
          <ul>
            <li>Vue.js 3</li>
            <li>GraphQL API</li>
            <li>RedisSearch</li>
            <li>Pinia Store</li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 Movie Library Explorer. Built with ❤️ using modern web technologies.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Footer component logic
</script>

<style scoped>
.nmle-footer {
  background-color: #000000;
  color: white;
  padding: 2rem 0 1rem;
  margin-top: auto;
  border-top: 1px solid #333;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3,
.footer-section h4 {
  margin-bottom: 1rem;
  color: #ffffff;
  font-weight: 600;
}

.footer-section p {
  color: #999;
  line-height: 1.6;
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  color: #999;
  margin-bottom: 0.5rem;
  padding-left: 1rem;
  position: relative;
}

.footer-section ul li::before {
  content: "•";
  color: #e50914;
  position: absolute;
  left: 0;
}

.footer-bottom {
  border-top: 1px solid #333;
  padding-top: 1rem;
  text-align: center;
}

.footer-bottom p {
  color: #666;
  margin: 0;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>
