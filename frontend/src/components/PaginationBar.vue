<template>
  <div class="pagination-footer">
    <span class="total-text">共{{ total }}条</span>
    <el-pagination
      :current-page="page"
      :page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="total"
      background
      layout="prev, pager, next, sizes, jumper"
      @update:current-page="emit('update:page', $event)"
      @update:page-size="emit('update:pageSize', $event)"
      @current-change="emit('change')"
      @size-change="emit('change')"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  total: number
  page: number
  pageSize: number
}>()

const emit = defineEmits<{
  (e: 'update:page', val: number): void
  (e: 'update:pageSize', val: number): void
  (e: 'change'): void
}>()
</script>

<style scoped>
.pagination-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  padding: 4px 2px;
}

.total-text {
  font-size: 13px;
  color: #606266;
}
</style>
