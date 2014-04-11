"""
nisyscfg_wrapper.py
"""

from ctypes import *

c_int_p = POINTER(c_int)
c_int8_p = POINTER(c_int8)
c_ubyte_p = POINTER(c_ubyte)
c_float_p = POINTER(c_float)
c_double_p = POINTER(c_double)
c_void_p_p = POINTER(c_void_p)
c_short_p = POINTER(c_short)

# nisyscfg dll path
system_dll_dir = "C:/Windows/System32/"
dll = windll.LoadLibrary(system_dll_dir+"nisyscfg.dll")

# enum defined in 'nisyscfg.h'
NISysCfgIncludeCachedResults = {
   'None': 				0L,
   'OnlyIfOnline': 		1L,
   'All': 				3L
}

# The initialization string may contain any combination of 1 or 2
# of the hostname, IP address, and/or MAC address.
NISysCfgSystemNameFormat = {
   'Hostname':			0x10L,       # "hostname"
   'HostnameIp':		0x12L,       # "hostname (1.2.3.4)"
   'HostnameMac':		0x13L,       # "hostname (01:02:03:04:05:06)"
   'Ip':				0x20L,       # "1.2.3.4"
   'IpHostname':       	0x21L,       # "1.2.3.4 (hostname)"
   'IpMac':				0x23L,       # "1.2.3.4 (01:02:03:04:05:06)"
   'Mac':				0x30L,       # "01:02:03:04:05:06"
   'MacHostname':		0x31L,       # "01:02:03:04:05:06 (hostname)"
   'FormatMacIp':		0x32L        # "01:02:03:04:05:06 (1.2.3.4)"
}

NISysCfgFileSystemMode = {
   'Default':                  0L,
   'Fat':                      1L,
   'Reliance':                 2L
}

NISysCfgComponentType = {
   'Standard':                   0L,          # Standard
   'Hidden':                     1L,          # Hidden
   'System':                     2L,          # System
   'Unknown':                    3L,          # Unknown
   'Startup':                    4L           # Startup
}

NISysCfgIncludeComponentTypes = {
   'AllVisible':            0x0000L,      # All visible
   'AllVisibleAndHidden':   0x0001L,      # Visible and hidden
   'OnlyStandard':          0x0002L,      # Only standard
   'OnlyStartup':           0x0003L       # Only startup
}

"""
typedef enum
{
   NISysCfgVersionSelectionHighest           = 0L,
   NISysCfgVersionSelectionExact             = 1L
} NISysCfgVersionSelectionMode;

typedef enum
{
   NISysCfgImportMergeItems                  = 0L,          // Source data "wins" in the case of overwrite conflicts
   NISysCfgImportDeleteConfigFirst           = 0x100000L,   // Delete product data at destination prior to copying
   NISysCfgImportPreserveConflictItems       = 0x200000L    // Destination data "wins" in the case of overwrite conflicts
} NISysCfgImportMode;

typedef enum
{
   NISysCfgReportXml                         = 0L,
   NISysCfgReportHtml                        = 1L,
   NISysCfgReportTechnicalSupportZip         = 2L
} NISysCfgReportType;

typedef enum
{
   NISysCfgBusTypeBuiltIn                    = 0L,
   NISysCfgBusTypePciPxi                     = 1L,
   NISysCfgBusTypeUsb                        = 2L,
   NISysCfgBusTypeGpib                       = 3L,
   NISysCfgBusTypeVxi                        = 4L,
   NISysCfgBusTypeSerial                     = 5L,
   NISysCfgBusTypeTcpIp                      = 6L,
   NISysCfgBusTypeCompactRio                 = 7L,
   NISysCfgBusTypeScxi                       = 8L,
   NISysCfgBusTypeCompactDaq                 = 9L,
   NISysCfgBusTypeSwitchBlock                = 10L
} NISysCfgBusType;

typedef enum
{
   NISysCfgHasDriverTypeUnknown              = -1L,
   NISysCfgHasDriverTypeNotInstalled         = 0L,
   NISysCfgHasDriverTypeInstalled            = 1L
} NISysCfgHasDriverType;

typedef enum
{
   NISysCfgIsPresentTypeUnknown              = -1L,
   NISysCfgIsPresentTypeNotPresent           = 0L,
   NISysCfgIsPresentTypePresent              = 1L
} NISysCfgIsPresentType;

typedef enum
{
   NISysCfgIpAddressModeStatic               = 1L,
   NISysCfgIpAddressModeDhcpOrLinkLocal      = 2L,
   NISysCfgIpAddressModeLinkLocalOnly        = 4L,
   NISysCfgIpAddressModeDhcpOnly             = 8L
} NISysCfgIpAddressMode;
"""

NISysCfgBool = {
   'False':                          0L,
   'True':                           1L
}

NISysCfgLocale = {
   'Default':                      0L,
   'ChineseSimplified':            2052L,
   'English':                      1033L,
   'French':                       1036L,
   'German':                       1031L,
   'Japanese':                     1041L,
   'Korean':                       1042L
}

NISysCfgFilterMode = {
   'All':                      1L,
   'Any':                      2L,
   'None':                     3L
}

"""
typedef enum
{
   NISysCfgServiceTypemDnsNiTcp              = 0L,
   NISysCfgServiceTypemDnsNiRealtime         = 1L,
   NISysCfgServiceTypemDnsNiSysapi           = 2L,
   NISysCfgServiceTypemDnsNiHttp             = 3L,
   NISysCfgServiceTypeLocalSystem            = 4L,
   NISysCfgServiceTypeLocalNetInterface      = 5L,
   NISysCfgServiceTypeLocalTimeKeeper        = 6L,
   NISysCfgServiceTypeLocalTimeSource        = 7L,
   NISysCfgServiceTypemDnsLxi                = 8L
} NISysCfgServiceType;

typedef enum
{
   NISysCfgAdapterTypeEthernet               = 1L,
   NISysCfgAdapterTypeWlan                   = 2L
} NISysCfgAdapterType;

typedef enum
{
   NISysCfgAdapterModeDisabled               = 1L,
   NISysCfgAdapterModeTcpIpEthernet          = 2L,
   NISysCfgAdapterModeDeterministic          = 4L,
   NISysCfgAdapterModeEtherCat               = 8L,
   NISysCfgAdapterModeTcpIpWlan              = 32L,
   NISysCfgAdapterModeTcpIpAccessPoint       = 64L
} NISysCfgAdapterMode;

typedef enum
{
   NISysCfgLinkSpeedNone                     = 0L,
   NISysCfgLinkSpeedAuto                     = 1L,
   NISysCfgLinkSpeed10mbHalf                 = 2L,
   NISysCfgLinkSpeed10mbFull                 = 4L,
   NISysCfgLinkSpeed100mbHalf                = 8L,
   NISysCfgLinkSpeed100mbFull                = 16L,
   NISysCfgLinkSpeedGigabitHalf              = 32L,
   NISysCfgLinkSpeedGigabitFull              = 64L,
   // Wireless 802.11 protocols (speeds)
   NISysCfgLinkSpeedWlan80211a               = 131072L,
   NISysCfgLinkSpeedWlan80211b               = 262144L,
   NISysCfgLinkSpeedWlan80211g               = 524288L,
   NISysCfgLinkSpeedWlan80211n               = 1048576L,
   NISysCfgLinkSpeedWlan80211n5GHz           = 2097152L
} NISysCfgLinkSpeed;

typedef enum
{
   NISysCfgPacketDetectionNone               = 0L,
   NISysCfgPacketDetectionInterrupt          = 1L,
   NISysCfgPacketDetectionPolling            = 2L 
} NISysCfgPacketDetection;

typedef enum
{
   NISysCfgConnectionTypeNone                = 0L,
   NISysCfgConnectionTypeInfrastructure      = 1L,
   NISysCfgConnectionTypeAdHoc               = 2L
} NISysCfgConnectionType;

typedef enum
{
   NISysCfgSecurityTypeNone                  = 0L,
   NISysCfgSecurityTypeNotSupported          = 1L,
   NISysCfgSecurityTypeOpen                  = 2L,
   NISysCfgSecurityTypeWep                   = 4L,
   NISysCfgSecurityTypeWpaPsk                = 8L,
   NISysCfgSecurityTypeWpaEap                = 16L, 
   NISysCfgSecurityTypeWpa2Psk               = 32L,
   NISysCfgSecurityTypeWpa2Eap               = 64L
} NISysCfgSecurityType;

typedef enum
{
   NISysCfgEapTypeNone                       = 0L,
   NISysCfgEapTypeEapTls                     = 1L,
   NISysCfgEapTypeEapTtls                    = 2L,
   NISysCfgEapTypeEapFast                    = 4L,
   NISysCfgEapTypeLeap                       = 8L,
   NISysCfgEapTypePeap                       = 16L
} NISysCfgEapType;

"""
# NOTE: For string properties, callers pass in a pointer to a buffer or array they have allocated.
NISysCfgResourceProperty = {
   # Read-only properties
   'IsDevice':                             16781312L,   # NISysCfgBool
   'IsChassis':                            16941056L,   # NISysCfgBool
   'NumberOfServices':                     17010688L,   # int
   'ConnectsToBusType':                    16785408L,   # NISysCfgBusType
   'VendorId':                             16789504L,   # unsigned int
   'VendorName':                           16793600L,   # char *
   'ProductId':                            16797696L,   # unsigned int
   'ProductName':                          16801792L,   # char *
   'SerialNumber':                         16805888L,   # char *
   'FirmwareRevision':                     16969728L,   # char *
   'IsNIProduct':                          16809984L,   # NISysCfgBool
   'IsSimulated':                          16814080L,   # NISysCfgBool
   'ConnectsToLinkName':                   16818176L,   # char *
   'HasDriver':                            16920576L,   # NISysCfgHasDriverType
   'IsPresent':                            16924672L,   # NISysCfgIsPresentType
   'SlotNumber':                           16822272L,   # int
   'SupportsInternalCalibration':          16842752L,   # NISysCfgBool
   'InternalCalibrationLastTime':          16846848L,   # NISysCfgTimestampUTC
   'InternalCalibrationLastTemp':          16850944L,   # double
   'SupportsExternalCalibration':          16859136L,   # NISysCfgBool
   'ExternalCalibrationLastTime':          16863232L,   # NISysCfgTimestampUTC
   'ExternalCalibrationLastTemp':          16867328L,   # double
   'RecommendedNextCalibrationTime':       16871424L,   # NISysCfgTimestampUTC
   'CalibrationComments':                  16961536L,   # char *
   'CurrentTemp':                          16965632L,   # double
   'PxiPciBusNumber':                      16875520L,   # unsigned int
   'PxiPciDeviceNumber':                   16879616L,   # unsigned int
   'PxiPciFunctionNumber':                 16883712L,   # unsigned int
   'PxiPciLinkWidth':                      16973824L,   # int
   'PxiPciMaxLinkWidth':                   16977920L,   # int
   'PxiPciSlotLinkWidth':                  16982016L,   # int
   'UsbInterface':                         16887808L,   # unsigned int
   'TcpHostName':                          16928768L,   # char *
   'TcpMacAddress':                        16986112L,   # char *
   'TcpIpAddress':                         16957440L,   # char *
   'TcpDeviceClass':                       17022976L,   # char *
   'GpibPrimaryAddress':                   16994304L,   # int
   'GpibSecondaryAddress':                 16998400L,   # int
   'ProvidesBusType':                      16932864L,   # NISysCfgBusType
   'ProvidesLinkName':                     16936960L,   # char *
   'NumberOfSlots':                        16826368L,   # int

   # Network Adapter properties
   'AdapterType':                          219332608L,  # NISysCfgAdapterType
   'AdapterMode':                          219160576L,  # NISysCfgAdapterMode
   'MacAddress':                           219168768L,  # char *
   'TcpIpRequestMode':                     219172864L,  # NISysCfgIpAddressMode
   'TcpIpv4Address':                       219181056L,  # char *
   'TcpIpv4Subnet':                        219189248L,  # char *
   'TcpIpv4Gateway':                       219193344L,  # char *
   'TcpIpv4DnsServer':                     219197440L,  # char *
   'TcpPreferredLinkSpeed':                219213824L,  # NISysCfgLinkSpeed
   'TcpPacketDetection':                   219258880L,  # NISysCfgPacketDetection
   'TcpPollingInterval':                   219262976L,  # unsigned int
   'IsPrimaryAdapter':                     219308032L,  # NISysCfgBool
   'EtherCatMasterId':                     219250688L,  # unsigned int

   # Wireless Network Adapter properties
   'WlanCurrentSsid':                      219377664L,  # char *
   'WlanCurrentConnectionType':            219381760L,  # NISysCfgConnectionType
   'WlanCurrentSecurityType':              219385856L,  # NISysCfgSecurityType
   'WlanCurrentEapType':                   219389952L,  # NISysCfgEapType
   'WlanCurrentLinkQuality':               219394048L,  # unsigned int
   'WlanBssid':                            219398144L,  # char *
   'WlanCountryCode':                      219406336L,  # int
   'WlanChannelNumber':                    219410432L,  # unsigned int
   'WlanSecurityIdentity':                 219414528L,  # char *
   'WlanSecurityKey':                      219418624L,  # char *

   # Time properties
   'CurrentTime':                          219279360L,   # NISysCfgTimestampUTC 
   'TimeZone':                             219471872L,   # char *

   # Counts for indexed properties
   'WlanAvailableCount':                   219365376L,  # unsigned int
   'NumberOfExperts':                      16891904L    # unsigned int
}

"""
typedef enum
{
   // Read-only properties
   NISysCfgIndexedPropertyServiceType                          = 17014784L,   // NISysCfgServiceType

   // Read-only properties
   NISysCfgIndexedPropertyWlanAvailableSsid                    = 219336704L,  // char *
   NISysCfgIndexedPropertyWlanAvailableBssid                   = 219443200L,  // char *
   NISysCfgIndexedPropertyWlanAvailableConnectionType          = 219340800L,  // NISysCfgConnectionType
   NISysCfgIndexedPropertyWlanAvailableSecurityType            = 219344896L,  // NISysCfgSecurityType
   NISysCfgIndexedPropertyWlanAvailableLinkQuality             = 219353088L,  // unsigned int
   NISysCfgIndexedPropertyWlanAvailableChannelNumber           = 219357184L,  // unsigned int
   NISysCfgIndexedPropertyWlanAvailableLinkSpeed               = 219361280L,  // NISysCfgLinkSpeed

   // Read-only properties
   NISysCfgIndexedPropertyExpertName                           = 16900096L,   // char *
   NISysCfgIndexedPropertyExpertResourceName                   = 16896000L,   // char *
   NISysCfgIndexedPropertyExpertUserAlias                      = 16904192L    // char *
} NISysCfgIndexedProperty;

typedef enum
{
   // Read-only properties
   NISysCfgSystemPropertyDeviceClass                           = 16941057L,   // char *
   NISysCfgSystemPropertyProductId                             = 16941058L,   // int
   NISysCfgSystemPropertyFileSystem                            = 16941060L,   // NISysCfgFileSystemMode
   NISysCfgSystemPropertyFirmwareRevision                      = 16941061L,   // char *
   NISysCfgSystemPropertyIsFactoryResetSupported               = 16941067L,   // NISysCfgBool
   NISysCfgSystemPropertyIsFirmwareUpdateSupported             = 16941068L,   // NISysCfgBool
   NISysCfgSystemPropertyIsLocked                              = 16941069L,   // NISysCfgBool
   NISysCfgSystemPropertyIsLockingSupported                    = 16941070L,   // NISysCfgBool
   NISysCfgSystemPropertyIsOnLocalSubnet                       = 16941072L,   // NISysCfgBool
   NISysCfgSystemPropertyIsRestartSupported                    = 16941076L,   // NISysCfgBool
   NISysCfgSystemPropertyMacAddress                            = 16941077L,   // char *
   NISysCfgSystemPropertyProductName                           = 16941078L,   // char *
   NISysCfgSystemPropertyOperatingSystem                       = 16941079L,   // char *
   NISysCfgSystemPropertySerialNumber                          = 16941080L,   // char *
   NISysCfgSystemPropertySystemState                           = 16941082L,   // char *

   // Read/Write properties
   NISysCfgSystemPropertyDnsServer                             = 16941059L,   // char *
   NISysCfgSystemPropertyGateway                               = 16941062L,   // char *
   NISysCfgSystemPropertyHostname                              = 16941063L,   // char *
   NISysCfgSystemPropertyIpAddress                             = 16941064L,   // char *
   NISysCfgSystemPropertyIpAddressMode                         = 16941065L,   // NISysCfgIpAddressMode
   NISysCfgSystemPropertyIsDst                                 = 16941066L,   // NISysCfgBool
   NISysCfgSystemPropertyIsRestartProtected                    = 16941073L,   // NISysCfgBool
   NISysCfgSystemPropertyHaltOnError                           = 16941074L,   // NISysCfgBool
   NISysCfgSystemPropertyRepositoryLocation                    = 16941084L,   // char *
   NISysCfgSystemPropertySubnetMask                            = 16941083L,   // char *
   NISysCfgSystemPropertySystemComment                         = 16941081L    // char *
} NISysCfgSystemProperty;

typedef enum
{
   // Write-only properties
   NISysCfgFilterPropertyIsDevice                              = 16781312L,   // NISysCfgBool
   NISysCfgFilterPropertyIsChassis                             = 16941056L,   // NISysCfgBool
   NISysCfgFilterPropertyServiceType                           = 17014784L,   // NISysCfgServiceType
   NISysCfgFilterPropertyConnectsToBusType                     = 16785408L,   // NISysCfgBusType
   NISysCfgFilterPropertyConnectsToLinkName                    = 16818176L,   // char *
   NISysCfgFilterPropertyProvidesBusType                       = 16932864L,   // NISysCfgBusType
   NISysCfgFilterPropertyVendorId                              = 16789504L,   // unsigned int
   NISysCfgFilterPropertyProductId                             = 16797696L,   // unsigned int
   NISysCfgFilterPropertyIsNIProduct                           = 16809984L,   // NISysCfgBool
   NISysCfgFilterPropertyIsSimulated                           = 16814080L,   // NISysCfgBool
   NISysCfgFilterPropertySlotNumber                            = 16822272L,   // int
   NISysCfgFilterPropertyHasDriver                             = 16920576L,   // NISysCfgHasDriverType
   NISysCfgFilterPropertyIsPresent                             = 16924672L,   // NISysCfgIsPresentType
   NISysCfgFilterPropertySupportsCalibration                   = 16908288L,   // NISysCfgBool
   NISysCfgFilterPropertyProvidesLinkName                      = 16936960L,   // char *
   NISysCfgFilterPropertyResourceName                          = 16896000L,   // char *
   NISysCfgFilterPropertyUserAlias                             = 16904192L    // char *
} NISysCfgFilterProperty;
"""
