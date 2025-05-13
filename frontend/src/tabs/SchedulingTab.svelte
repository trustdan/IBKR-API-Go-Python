<script lang="ts">
  // This is a placeholder component
</script>

<div class="scheduling-tab">
  <header>
    <h1>Trading Schedule</h1>
    <p>Configure when your trading system operates.</p>
  </header>

  <div class="placeholder-content">
    <div class="card">
      <h2>Trading Hours</h2>
      <p>Set the times when the system will allow trading.</p>
      <div class="form-placeholder">
        <div class="form-row">
          <label>Enable schedule</label>
          <div class="toggle active"></div>
        </div>
        <div class="form-row">
          <label>Start time:</label>
          <div class="input-placeholder"></div>
        </div>
        <div class="form-row">
          <label>End time:</label>
          <div class="input-placeholder"></div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>Trading Days</h2>
      <p>Select which days of the week to allow trading.</p>
      <div class="days-grid">
        <div class="day-item active">Mon</div>
        <div class="day-item active">Tue</div>
        <div class="day-item active">Wed</div>
        <div class="day-item active">Thu</div>
        <div class="day-item active">Fri</div>
        <div class="day-item">Sat</div>
        <div class="day-item">Sun</div>
      </div>
    </div>
  </div>
</div>

<style>
  .scheduling-tab {
    padding: 1rem;
    max-width: 1000px;
    margin: 0 auto;
  }

  header {
    margin-bottom: 2rem;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #1e293b;
  }

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    color: #1e293b;
  }

  p {
    color: #64748b;
    margin: 0 0 1rem 0;
  }

  .placeholder-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }

  .card {
    background-color: #ffffff;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
  }

  .form-placeholder {
    margin-top: 1.5rem;
  }

  .form-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .form-row label {
    font-weight: 500;
    color: #64748b;
  }

  .input-placeholder {
    width: 150px;
    height: 30px;
    background-color: #f1f5f9;
    border-radius: 0.25rem;
  }

  .toggle {
    width: 50px;
    height: 24px;
    background-color: #e2e8f0;
    border-radius: 12px;
    position: relative;
  }

  .toggle.active {
    background-color: #10b981;
  }

  .toggle.active::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    background-color: white;
    border-radius: 50%;
    top: 2px;
    left: calc(100% - 22px);
    transition: left 0.2s;
  }

  .toggle::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    background-color: white;
    border-radius: 50%;
    top: 2px;
    left: 2px;
    transition: left 0.2s;
  }

  .days-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.5rem;
    margin-top: 1.5rem;
  }

  .day-item {
    background-color: #f1f5f9;
    border-radius: 0.25rem;
    padding: 0.5rem 0;
    text-align: center;
    font-weight: 500;
    color: #64748b;
  }

  .day-item.active {
    background-color: #3b82f6;
    color: white;
  }

  @media (max-width: 768px) {
    .placeholder-content {
      grid-template-columns: 1fr;
    }
  }
</style>
