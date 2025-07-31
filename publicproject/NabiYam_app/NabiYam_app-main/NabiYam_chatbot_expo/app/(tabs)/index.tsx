import React from 'react';
import { StyleSheet, Text, View, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
// SafeAreaView를 import 합니다.
import { SafeAreaView } from 'react-native-safe-area-context';

export default function HomeScreen() {
  // 최상위 컴포넌트를 SafeAreaView로 변경합니다.
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        {/* 앱 헤더 */}
        <View style={styles.appHeader}>
          <Text style={styles.appTitle}>나비얌</Text>
          <View style={styles.notificationIcon} />
        </View>

        {/* 배너 */}
        <LinearGradient colors={['#4A90E2', '#7B68EE']} style={styles.bannerSection}>
          <Text style={styles.bannerText}>인천시 가맹점 확인해보세요</Text>
          <Text style={styles.bannerTitle}>인천시 급식카드 결제 OPEN</Text>
        </LinearGradient>

        {/* 콘텐츠 */}
        <View style={styles.contentSection}>
          <Text style={styles.campaignHeader}>캠페인</Text>
          <Text style={styles.campaignSubtitle}>캠페인 참여하고 따뜻한 혜택 받아가세요</Text>
          <LinearGradient colors={['#FFF8E1', '#FFE082']} style={styles.mealCard}>
            <View>
              <Text style={styles.mealTitle}>도시락 한컵</Text>
              <Text style={styles.mealSubtitle}>마음 한 숟갈</Text>
              <View style={styles.mealTagContainer}>
                 <Text style={styles.mealTag}>인천광역시 내 매장 전용</Text>
              </View>
            </View>
            <View style={styles.mealImage} />
          </LinearGradient>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// 스타일시트는 이전과 동일합니다.
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'white' },
  appHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    padding: 15, 
    borderBottomWidth: 1, 
    borderBottomColor: '#e0e0e0' 
  },
  appTitle: { fontSize: 24, fontWeight: 'bold' },
  notificationIcon: { width: 24, height: 24, backgroundColor: '#666', borderRadius: 4 },
  bannerSection: { padding: 20, alignItems: 'center' },
  bannerText: { fontSize: 16, color: 'white', marginBottom: 8 },
  bannerTitle: { fontSize: 20, fontWeight: 'bold', color: 'white' },
  contentSection: { padding: 20 },
  campaignHeader: { fontSize: 18, fontWeight: 'bold', marginBottom: 8 },
  campaignSubtitle: { fontSize: 14, color: '#666', marginBottom: 20 },
  mealCard: { borderRadius: 15, padding: 20, flexDirection: 'row', justifyContent: 'space-between' },
  mealTitle: { fontSize: 22, fontWeight: 'bold', color: '#333' },
  mealSubtitle: { fontSize: 18, color: '#555', marginTop: 5 },
  mealTagContainer: { backgroundColor: 'rgba(0,0,0,0.7)', paddingVertical: 8, paddingHorizontal: 15, borderRadius: 20, marginTop: 15, alignSelf: 'flex-start' },
  mealTag: { color: 'white', fontSize: 12 },
  mealImage: { width: 80, height: 80, backgroundColor: '#D4AF37', borderRadius: 10 },
});