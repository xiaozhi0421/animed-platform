<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <div class="brand-icon">
          <svg viewBox="0 0 500 500" fill="none" stroke="#409eff" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" style="width:48px;height:48px;">
            <path d="M399.686,108.48c-0.954-3.094-3.28-5.456-6.22-6.278c-10.102-2.854-18.566-10.162-23.222-20.083c-0.794-1.674-1.65-3.29-2.601-4.866c-4.041-6.689-10.037-11.731-17.064-14.42c-6.529-2.497-11.068-6.278-15.285-9.976c-0.453-8.863-2.294-33.415-9.322-50.212c-0.55-1.317-1.713-2.27-3.086-2.555c-1.408-0.291-2.846,0.139-3.879,1.124c-6.836,6.672-19.793,22.122-25.838,46.649c-26.691,12.207-34.69,38.237-34.69,56.239c0,5.59,1.16,10.882,2.828,15.963c-13.332,6.22-26.082,19.46-38.084,40.669l-61.662,74.175l0.033,0.015c-23.381,21.372-39.021,59.623-39.021,103.404c0,9.139,0.81,17.466,2.083,25.28c-0.272,0.386-0.69,0.615-0.936,1.034c-20.146,33.32-17.886,29.647-22.619,39.806c-9.44,25.241-4.175,51.998,10.583,67.34c20.15,20.949,41.785,25.031,49.638,24.561c15.998,0.271,13.009,0.273,98.143-28.422c5.637-1.9,8.854-7.901,7.236-13.682c-1.645-5.975-7.869-9.466-13.844-7.795c-85.793,24.045-83.326,24.738-97.273,21.055c-1.197-0.411-45.578-20.399-15.755-64.13c14.3,21.183,36.196,31.894,61.14,32.768v0.29h90.295c7.124,0,12.924-4.76,12.924-10.631c0-9.324-5.072-18.162-13.815-24.068c-4.069-2.763-8.788-4.677-13.749-5.835c6.383-11.108,10.795-24.6,12.637-40.53l24.559,76.741c0.888,2.588,3.33,4.324,6.062,4.324h42.058c8.207,0,14.865-4.768,14.865-10.624c0-9.332-5.83-18.155-15.898-24.076c-5.93-3.498-13.007-5.591-20.426-6.489l-10.645-39.49l-5.172-87.634c20.359-21.441,33.024-45.532,24.545-90.848c-3.945-20.971,10.631-30.634,13.346-32.243c2.456-0.848,4.91-1.787,7.367-2.529c3.814-1.154,7.662-2.795,11.325-5.281c2.218-1.514,10.132-7.225,16.79-19.803C399.521,114.595,400.606,111.559,399.686,108.48z"/>
          </svg>
        </div>
        <h2>选择注册类型</h2>
        <p>请选择您的身份类型进行注册</p>
      </div>
      <div class="role-cards">
        <div class="role-card campus" @click="$router.push('/register/student')">
          <el-icon><Reading /></el-icon>
          <h3>学生注册</h3>
          <p>动物医学学院学生，通过学号注册</p>
        </div>
        <div class="role-card campus" @click="$router.push('/register/teacher')">
          <el-icon><User /></el-icon>
          <h3>教师注册</h3>
          <p>动物医学学院教师，通过教师号注册</p>
        </div>
      </div>
      <div class="back-link">
        <router-link to="/login">← 返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-page {
  width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #0f0c29 0%, #1d1e3a 30%, #0d7377 70%, #14b8a6 100%);
}
.register-container {
  width: 520px; padding: 40px; background: #fff; border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.register-header {
  text-align: center; margin-bottom: 30px;
  .brand-icon { margin-bottom: 12px; }
  h2 { font-size: 22px; color: #1a1a2e; margin-bottom: 8px; font-weight: 700; }
  p { color: #94a3b8; font-size: 14px; }
}
.role-cards {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}
.role-card {
  padding: 28px 20px; border-radius: 14px; text-align: center; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1); border: 2px solid transparent;
  .el-icon { font-size: 40px; margin-bottom: 14px; }
  h3 { font-size: 17px; margin-bottom: 8px; font-weight: 600; }
  p { font-size: 12px; color: #94a3b8; line-height: 1.5; }
  &:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,0.1); }
  &.campus {
    background: linear-gradient(135deg, #eef2ff, #f0f5ff);
    .el-icon { color: #6366f1; }
    h3 { color: #4338ca; }
    &:hover { border-color: #6366f1; }
  }
}
.back-link { text-align: center; margin-top: 24px; a { color: #6366f1; text-decoration: none; font-size: 14px; &:hover { text-decoration: underline; } } }
</style>
