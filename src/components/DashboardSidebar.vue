<script setup>
// 展示三层经营摘要；只读取父级快照，通过事件请求层级切换。
import { computed } from 'vue';
import Icon from './Icon.vue';
import { number, area, occupancy, vacant } from '../data/state.js';
const props = defineProps(['config', 'level', 'mode', 'data', 'selected', 'entering']);
const emit = defineEmits(['back', 'focus']);
const previewUrl = import.meta.env.BASE_URL + 'assets/a1-preview.png';
const focusBuilding = props.config.demoDesign.focusBuilding;
const selectedData = computed(() => props.data.byBuilding[props.selected]);
const currentIdentity = computed(() =>
  props.config.demoDesign.buildingIdentities.find((o) => o.id === props.selected),
);
const back = () => emit('back');
const focus = () => emit('focus');
const formatArea = area,
  formatNumber = number;
const formatAreaFixed = (value) =>
  area(value, props.config.demoDesign.contentDefinitions.spaceUsage.precision, false);
const values = computed(() => props.data[props.level === 'campus' ? 'campus' : 'building']);
const metrics = computed(() => [
  {
    label: props.level === 'campus' ? '楼宇总数' : '楼层数',
    value: number(props.level === 'campus' ? values.value.buildings : values.value.floors),
    unit: props.level === 'campus' ? '栋' : '层',
    icon: 'building',
  },
  { label: '建筑面积', value: area(values.value.grossAreaM2), unit: '万㎡', icon: 'area' },
  { label: '出租率', value: number(occupancy(values.value)), unit: '%', icon: 'rate' },
  { label: '入驻企业', value: number(values.value.enterprises), unit: '家', icon: 'people' },
]);
</script>

<template>
  <aside class="rail" :inert="entering" :style="{ width: 'var(--rail-width)' }">
    <header class="brand-header">
      <h1>{{ config.project.title }}</h1>
      <div class="brand-line">
        <span>武汉 · 光谷</span
        ><span class="badge"
          >{{ level === 'city' ? '区域概念' : '示范园区' }} ·
          {{ mode === 'demo' ? '演示数据' : '暂无数据' }}</span
        >
      </div>
      <div v-if="level === 'city'" class="city-caption">
        <h2>区域总览</h2>
        <p>{{ config.demoDesign.region.name }}</p>
      </div>
      <div v-else-if="level === 'campus'" class="level-caption">园区总览</div>
      <nav v-else class="breadcrumb">
        <button @click="back">园区总览</button><span>/</span><strong>重点楼宇</strong>
      </nav>
    </header>
    <div v-if="level === 'building'" class="focus-title">
      <span>{{ focusBuilding.id }}</span>
      <h2>{{ focusBuilding.name }}</h2>
    </div>
    <section v-if="level !== 'city'" class="kpis" aria-label="关键指标">
      <article v-for="m in metrics" :key="m.label" class="kpi">
        <Icon :name="m.icon" />
        <div>
          <div class="metric-value">
            <strong>{{ m.value }}</strong
            ><span v-if="m.value !== '—'">{{ m.unit }}</span>
          </div>
          <p>{{ m.label }}</p>
        </div>
      </article>
    </section>
    <template v-if="level === 'city'">
      <section class="industry-section">
        <h3>产业方向</h3>
        <div class="category-grid">
          <div
            v-for="(text, i) in config.demoDesign.contentDefinitions.industryDirections.labels"
            :key="text"
          >
            <Icon :name="['code', 'chip', 'briefcase'][i]" /><span>{{ text }}</span>
          </div>
        </div>
      </section>
      <section class="city-park-section">
        <h3>重点园区</h3>
        <div class="resource-card">
          <button class="resource-heading" @click="back">
            <span>{{ config.demoDesign.region.campusName }}</span
            ><span>›</span>
          </button>
          <div class="city-metrics">
            <article
              v-for="(m, i) in [
                {
                  label: '楼宇数',
                  value: formatNumber(data.campus.buildings),
                  unit: '栋',
                  icon: 'building',
                },
                {
                  label: '建筑面积',
                  value: formatArea(data.campus.grossAreaM2),
                  unit: '万㎡',
                  icon: 'area',
                },
                {
                  label: '出租率',
                  value: formatNumber(occupancy(data.campus)),
                  unit: '%',
                  icon: 'rate',
                },
                {
                  label: '入驻企业',
                  value: formatNumber(data.campus.enterprises),
                  unit: '家',
                  icon: 'people',
                },
              ]"
              :key="m.label"
            >
              <Icon :name="m.icon" />
              <div>
                <strong>{{ m.value }}</strong
                ><small v-if="m.value !== '—'">{{ m.unit }}</small>
                <p>{{ m.label }}</p>
              </div>
            </article>
          </div>
          <p v-if="mode === 'no-data'" class="city-empty-note">暂无园区经营数据</p>
          <button class="city-enter" @click="back">进入园区 <span>›</span></button>
        </div>
      </section>
    </template>
    <template v-else-if="level === 'campus'">
      <section class="industry-section composition-section">
        <h3>产业构成 <small>演示占比</small></h3>
        <div class="industry-bars" aria-label="产业构成横向柱状图">
          <div v-for="item in data.industryComposition" :key="item.id" class="industry-row">
            <span>{{ item.label }}</span>
            <div class="industry-track">
              <i
                :style="{
                  width:
                    item.share === null
                      ? '0%'
                      : (item.share / config.demoDesign.industryComposition.axisMaximumPercent) *
                          100 +
                        '%',
                }"
              ></i>
            </div>
            <strong
              >{{ formatNumber(item.share) }}<small v-if="item.share !== null">%</small></strong
            >
          </div>
          <div class="industry-axis"><span>0%</span><span>20%</span><span>40%</span></div>
        </div>
        <p v-if="mode === 'no-data'" class="composition-empty">暂无产业构成数据</p>
      </section>
      <section class="resource-card" :data-building-id="selected">
        <button
          class="resource-heading"
          :disabled="selected !== focusBuilding.id"
          @click="selected === focusBuilding.id && focus()"
        >
          <span
            >{{ selected }}
            {{ selected === focusBuilding.id ? focusBuilding.name : currentIdentity?.role }}</span
          ><span v-if="selected === focusBuilding.id" aria-hidden="true">›</span
          ><small v-else>已选楼宇</small>
        </button>
        <div class="selected-building-summary">
          <div class="building-portrait">
            <img
              v-if="selected === focusBuilding.id"
              :src="previewUrl"
              alt="A1科创大厦实际模型预览"
            /><template v-else
              ><Icon name="building" /><b>{{ selected }}</b></template
            >
          </div>
          <dl class="selected-building-metrics">
            <div>
              <Icon name="building" />
              <dd>{{ formatNumber(selectedData.floors) }} <small>层</small></dd>
            </div>
            <div>
              <Icon name="area" />
              <dd>{{ formatArea(selectedData.grossAreaM2) }} <small>万㎡</small></dd>
            </div>
            <div>
              <Icon name="rate" />
              <dd>
                {{ formatNumber(occupancy(selectedData)) }}<small v-if="mode === 'demo'">%</small>
              </dd>
            </div>
            <div>
              <Icon name="people" />
              <dd>{{ formatNumber(selectedData.enterprises) }} <small>家</small></dd>
            </div>
          </dl>
        </div>
      </section>
    </template>
    <template v-else>
      <section class="space-section">
        <h3>空间利用</h3>
        <dl>
          <div>
            <dt>出租率</dt>
            <dd>
              {{ formatNumber(occupancy(data.building)) }}<span v-if="mode === 'demo'">%</span>
            </dd>
          </div>
          <div>
            <dt>已租面积</dt>
            <dd>{{ formatAreaFixed(data.building.rentedAreaM2) }} <small>万㎡</small></dd>
          </div>
          <div>
            <dt>可租面积</dt>
            <dd>{{ formatAreaFixed(data.building.rentableAreaM2) }} <small>万㎡</small></dd>
          </div>
          <div>
            <dt>可租空置面积</dt>
            <dd>{{ formatAreaFixed(vacant(data.building)) }} <small>万㎡</small></dd>
          </div>
        </dl>
      </section>
      <section class="building-industry">
        <h3>入驻产业</h3>
        <div v-if="mode === 'demo'" class="category-grid compact">
          <div
            v-for="(text, i) in config.demoDesign.contentDefinitions.buildingIndustries.labels"
            :key="text"
          >
            <Icon :name="['code', 'chip', 'briefcase'][i]" /><span>{{ text }}</span>
          </div>
        </div>
        <p v-else class="empty-state">暂无产业数据</p>
      </section>
      <section class="services">
        <h3>配套服务</h3>
        <div class="category-grid compact">
          <div
            v-for="(text, i) in config.demoDesign.contentDefinitions.services.labels"
            :key="text"
          >
            <Icon :name="['meeting', 'parking', 'bus'][i]" /><span>{{ text }}</span>
          </div>
        </div>
      </section>
      <button class="back-button" @click="back"><Icon name="back" />返回园区</button>
    </template>
  </aside>
</template>
